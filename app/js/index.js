var selected_classes = [];

var object = {
    "domain": "inforestudante.ipc.pt",
    "student_number": null,
    "password": null,
    "classes": []
}

$(document).ready(function () {

    $("#classes").hide()
    $("#log").hide()

    $("#login button").click(function () {
        object.student_number = $("#username").val()
        if(object.student_number == ""){
            alert("Por favor insere o teu email")
            return
        }
        if (object.student_number.includes("@isec.pt"))
            object.student_number = object.student_number.replace("@isec.pt", "")
        object.password = $("#password").val();
        if(object.password == ""){
            alert("Por favor insere a tua palavra-chave")
            return
        }
        var btnObj = $(this);
        btnObj.html("A iniciar sessão...")
        btnObj.prop("disabled", true)
        window.electronAPI.getCadeiras(object).then(function (result) {
            $("#login").hide()
            $("#classes").show()
            for(item of result.cadeiras){
                $("#classes .subjects").append(`
                    <div class="class">
                        <div class="name">${item}</div>
                        <input type="text" placeholder="T1" class="turma teorica">
                        <input type="text" placeholder="P1" class="turma pratica">
                        <input type="text" placeholder="TP1" class="turma teoricopratica">
                    </div>
                `)
            }
            $("#classes button").click(function () {
                for (item of $("#classes .subjects .class")) {
                    var name = $(item).find(".name").html()
                    var teorica = $(item).find(".teorica").val().toUpperCase()
                    var pratica = $(item).find(".pratica").val().toUpperCase()
                    var teoricopratica = $(item).find(".teoricopratica").val().toUpperCase()
                    if (teorica != "" || pratica != "" || teoricopratica != "") {
                        if(teorica == "") teorica = []
                        else teorica = [teorica]
                        if(pratica == "") pratica = []
                        else pratica = [pratica]
                        if(teoricopratica == "") teoricopratica = []
                        else teoricopratica = [teoricopratica]
                        selected_classes.push({
                            "name": name,
                            "practice": pratica,
                            "theoric": teorica,
                            "theoric_practice": teoricopratica
                        })
                    }
                }
                object.classes = selected_classes
                $("#classes").hide()
                $("#log").show()
                window.electronAPI.runScript(object).then(function (result) {
                    $(".loader").hide()
                    $("#log .output").show()
                    $("#log button").attr("disabled", false)
                    for(item of result){
                        $("#log .output").append(`<p>${item}</p>`)
                    }
                    $("#log .output").scrollTop($("#log .output")[0].scrollHeight)
                    $("#log button").click(function () {
                        window.close()
                    })
                })
            })
        }).catch(function (error) {
            if(error == 500){
                alert("Ocorreu um erro ao iniciar sessão. Por favor tenta novamente")
            }
            btnObj.html("Iniciar sessão")
            btnObj.prop("disabled", false)
        })
    });
});