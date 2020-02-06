

function displayConfigSection(sectionClass) {
    var configInputs = document.querySelectorAll(".config-inputs");
    for (i in configInputs) {
        $( configInputs[i] ).hide();
        if (configInputs[i].className.includes(sectionClass)) {
            $( configInputs[i] ).fadeIn();
        }
    }        
}

function showGlobalCmds() {
    var container = document.querySelector("#globalCmdsContainer");
    var cmds = $( "#globalCmds" ).val().split(",");
    
    for (i in cmds) {
        if (cmds[i]) {
            container.innerHTML += `<div style='margin-right: 10px;' class='card'>${cmds[i]}<span class="remove-command">X</span></div>`;
        }
    }
}

function submitForm(formID) {
    document.getElementByID(formID).submit()
}

function dropdown(id) {
    var section = document.querySelector(`[int-number="${id}"]`);
    var dropdownBottom = section.querySelector(".dropdown-bottom");
    var arrow = section.querySelector(".arrow");

    if (dropdownBottom.style.display === "inline-flex") { 
        $( arrow ).attr("class", "arrow down")
        $( dropdownBottom ).css("display", "inline-flex")
        $( dropdownBottom ).slideUp(600);
    } else {                                     
        $( arrow ).attr("class", "arrow up")
        $( dropdownBottom ).slideDown(600);
        $( dropdownBottom ).css("display", "inline-flex")
    }
}

function displayTerminal() {
    term = new Terminal();
    term.open(document.getElementById('terminal'));
    var termURI = document.location.href + "term";
    var csrfToken = $( 'input[name=csrfmiddlewaretoken]' ).val();
    var intro = [
        "LANwhiz CLI Interface",
    ];
    term.writeln("");

    prompt = function() {
        $.post(termURI, {
            csrfmiddlewaretoken: csrfToken
        }, function (resp) {
            term.write(resp.prompt);
        });
    }
    
    var cmd = "";

    term.onKey(e => {
        const printable = !e.domEvent.altKey && !e.domEvent.altGraphKey && !e.domEvent.ctrlKey && !e.domEvent.metaKey;
        
    
        if (e.domEvent.keyCode === 13) {
            $.post(termURI, {
                csrfmiddlewaretoken: csrfToken, 
                cmd: cmd 
            } , function(response) {
                termPrompt = response.prompt
                response = response.cmd_out.split("\n");
                term.writeln("");
                for (var i in response) {
                    term.writeln(response[i])
                }
                cmd = "";
                term.write
            })

        } else if (e.domEvent.keyCode === 8) {
            // Do not delete the prompt
            if (term._core.buffer.x > 2) {
                term.write('\b \b');
            }
            cmd = cmd.slice(NaN,-1)
        } else if (printable) {
            term.write(e.key);
            cmd += e.key;
        }
    });

}

$( document ).ready(function() {
    displayTerminal();
    showGlobalCmds();
    displayConfigSection("access");
});