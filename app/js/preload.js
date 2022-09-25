const { contextBridge, ipcRenderer } = require('electron')
let {PythonShell} = require('python-shell')

contextBridge.exposeInMainWorld('electronAPI', {
    getCadeiras: function (data) {
        let options = {
            mode: 'text',
            pythonOptions: ['-u'],
            args: JSON.stringify(data)
        };
        let script = PythonShell.run('../login.py', options, function (err, results) {
            if (err) throw err;
        });
        return new Promise((resolve, reject) => {
            script.on('message', function (message) {
                message = JSON.parse(message)
                if(message.status == 500){
                    reject(500)
                } else {
                    resolve(message)
                }
            })
        })
    },
    runScript: function (data) {
        messages = []
        let options = {
            mode: 'text',
            pythonOptions: ['-u'],
            args: JSON.stringify(data)
        };
        let script = PythonShell.run('../rouba_turmas.py', options, function (err, results) {
            if (err) throw err;
        });
        script.on('message', function (message) {
            messages.push(message)
        })
        return new Promise((resolve, reject) => {
            script.on('close', function (message) {
                resolve(messages)
            })
        })
    }
})