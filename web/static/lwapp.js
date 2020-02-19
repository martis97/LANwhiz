

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

function showACLCards() {
    var noneAssigned = '<span style="font-size: 10px;">None Assigned</span>';
    var interfaces = document.querySelectorAll(".interface");
    interfaces.forEach( interface => {
        var $int = $( interface );
        var interfaceTitle = $int.find(".interface-title").text().replace("/", "\\/");
        var $inboundContainer = $int.find(`#${interfaceTitle}-inbound-container`);
        var $outboundContainer = $int.find(`#${interfaceTitle}-outbound-container`);
        var inboundACLs = $int.find(`#id_${interfaceTitle}-inbound_acl`).val();
        var outboundACLs = $int.find(`#id_${interfaceTitle}-outbound_acl`).val();

        if (inboundACLs) {
            inboundACLs.split(",").forEach( cmd => {
                if (cmd) {
                    cmd = `<div style='margin-right: 10px;' class='card acl-in'>${cmd}<span class="remove-command">X</span></div>`;
                    $inboundContainer.append(cmd)
                }
            });
        } else {
            $inboundContainer.append(noneAssigned)
        }
        if (outboundACLs) {
            outboundACLs.split(",").forEach( cmd => {
                if (cmd) {
                    cmd = `<div style='margin-right: 10px;' class='card  acl-out'>${cmd}<span class="remove-command">X</span></div>`;
                    $outboundContainer.append(cmd)
                }
            });
        } else {
            $outboundContainer.append(noneAssigned)
        }
    })
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
    var termPrompt = "";
    var error = false;

    var intro = [
        "LANwhiz CLI Interface",
        "\nUse for various 'show' commands and other bespoke configuration",
        "\nNOTE: Changing the config areas which are overseen by the program will",
        "require a config sync once finished.\n",
        "Connecting...\n"
    ];
    for (i in intro) term.writeln(intro[i]);
    

    $.post(termURI, {
        csrfmiddlewaretoken: csrfToken
    }, response => {
        if ('error' in response) {
            error = true;
            term.writeln("Error: " + response.error);
        } else {
            term.writeln("Connected!\n\n")
            termPrompt = response.prompt;
            term.write(termPrompt);
        }
    });
    
    cmd = "";

    term.onKey(e => {
        const printable = !e.domEvent.altKey && !e.domEvent.altGraphKey && !e.domEvent.ctrlKey && !e.domEvent.metaKey;
        
        if (e.domEvent.keyCode === 13) {
            if (!termPrompt || error) return;
            if (cmd) {
                $.post(termURI, {
                    csrfmiddlewaretoken: csrfToken, 
                    cmd: cmd 
                } , response => {
                    termPrompt = response.prompt
                    response = response.cmd_out;
                    term.writeln("");
                    for (var i in response) term.writeln(response[i]);
                    cmd = "";

                    term.write(termPrompt)
                })
            } else {
                term.write("\n" + "\b".repeat(term._core.buffer.x) + termPrompt)
            }
        } else if (e.domEvent.keyCode === 8) {
            // Do not delete the prompt
            if (term._core.buffer.x > termPrompt.length) {
                term.write('\b \b');
                cmd = cmd.slice(NaN,-1)
            }
        } else if (printable) {
            term.write(e.key);
            cmd += e.key;
        }
        
    });

}


$( document ).ready(function() {
    showACLCards();
    displayTerminal();
    showGlobalCmds();
    displayConfigSection("access");
});