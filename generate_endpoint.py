#!/usr/bin/python3

import inquirer
from colorama import Fore, Back, Style

JS_POST_TEMPLATE="""
var fd = new FormData();
{}
fetch('{}', {{
    method: "POST",
    body: fd
}})
.then(data => {{
    if (data.status === 200)
        return data.json()
    else {{
        console.log("ERROR ", data.status)
        return data.json()
    }}
}})
.then(data => {{
    console.log(data);
}})
"""

JS_GET_TEMPLATE="""
fetch({})
.then((data) => {{
    if (data.status === 200)
        return data.json()
    else {{
        console.log("ERROR ", data.status)
        return data.json()
    }}
}})
.then((data) => {{
    console.log(data);
}})
"""

GO_HANDLER_TEMPLATE="""
func {}(appContext *storageapi.AppContext, r *http.Request{}) {} {{
    {}
    {}
    {}
}}
"""

if __name__ == '__main__':

    questions = [
        inquirer.List('method', message='Request method?', choices=['GET', 'POST']),
        inquirer.Text('endpointname', message='Endpoint name?', validate=lambda x, y: y != ''),
        inquirer.List('wrappertype', message='Wrapper type?', choices=['JSONWrapper', 'UserJSONWrapper', 'FileWrapper', 'UserFileWrapper']),
        inquirer.Text('handlerspackage', message='Handlers package?', default="handlers"),
    ]

    answers = inquirer.prompt(questions)

    answers1 = {'varname': 'a'}
    variables = []
    while answers1['varname'] != '':
        answers1 = inquirer.prompt([inquirer.Text('varname', message='Add variable? (empty ends)')])
        if answers1['varname'] != '':
            variables.append(answers1['varname'])

    print(Fore.GREEN + 'JAVASCRIPT' + Style.RESET_ALL)

    if answers['method'] == "GET":
        fullUrl = "'/api/"+answers['endpointname'].lower()+"?"+"+'&".join(map(lambda x: x+"='+"+x, variables))
        print(JS_GET_TEMPLATE.format(fullUrl))
    elif answers['method'] == "POST":
        fdvars = "\n".join(map(lambda x: "fd.append('"+x+"', "+x+");", variables))
        print(JS_POST_TEMPLATE.format(fdvars, "/api/"+answers['endpointname'].lower()))

    print(Fore.GREEN + 'GO MAIN' + Style.RESET_ALL)
    print('r.Handle("/api/'+answers['endpointname'].lower() +
        '", webframework.'+answers['wrappertype']+'{Ctx: ctx, Handle: '+answers['handlerspackage']+'.'+answers['endpointname'] +
        (', Tokens: &tokens' if answers['wrappertype'][:4] == "User" else "") +
        '}).Methods("'+answers['method']+'")')

    print(Fore.GREEN + 'GO HANDLER' + Style.RESET_ALL)
    print(GO_HANDLER_TEMPLATE.format(answers['endpointname'], ", user int" if answers['wrappertype'][:4] == "User" else "",
        "(io.Reader, string, int)" if "File" in answers['wrappertype'] else "(interface{}, int)",
        ("\n".join(map(lambda var: var + ' := r.PostFormValue("'+var+'")', variables))) if answers['method'] == "POST" else
            ("\n".join(map(lambda var: var + ' := r.URL.Query().Get("'+var+'")', variables))),
        "fmt.Println(" + ", ".join(variables) + ")",
        "return nil, "", 500" if "File" in answers['wrappertype'] else "return map[string]interface{}{\"status\": \"ok\"}, 200"))