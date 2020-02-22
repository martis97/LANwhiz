

function displayConfigSection(sectionClass) {
    const configInputs = document.querySelectorAll(".config-inputs");

    for (i in configInputs) {
        $( configInputs[i] ).hide();
        if (configInputs[i].className.includes(sectionClass)) {
            $( configInputs[i] ).fadeIn();
        }
    }        
}

function showGlobalCmds() {
    const container = document.querySelector("#globalCmdsContainer");
    const cmds = $( "#globalCmds" ).val().split(",");
    
    for (i in cmds) {
        if (cmds[i]) {
            container.innerHTML += `<div style='margin-right: 10px;' class='card'>${cmds[i]}<span class="remove-command">X</span></div>`;
        }
    }
}

function showACLCards() {
    const noneAssigned = '<span style="font-size: 10px;">None Assigned</span>'
    const interfaces = document.querySelectorAll(".interface")

    interfaces.forEach( interface => {
        const $int = $( interface )
        const interfaceTitle = $int.find(".interface-title").text().replace("/", "\\/")
        const $inboundContainer = $int.find(`#${interfaceTitle}-inbound-container`)
        const $outboundContainer = $int.find(`#${interfaceTitle}-outbound-container`)
        const inboundACLs = $int.find(`#id_${interfaceTitle}-inbound_acl`).val()
        const outboundACLs = $int.find(`#id_${interfaceTitle}-outbound_acl`).val()

        if (inboundACLs) {
            inboundACLs.split(",").forEach( acl => {
                if (acl) {
                    acl = `<div style='margin-right: 10px;' class='card acl-in'>${acl}<span class="remove acl">X</span></div>`
                    $inboundContainer.append(acl)
                }
            });
        } else {
            $inboundContainer.append(noneAssigned)
        }
        
        if (outboundACLs) {
            outboundACLs.split(",").forEach( acl => {
                if (acl) {
                    cmd = `<div style='margin-right: 10px;' class='card  acl-out'>${acl}<span class="remove acl">X</span></div>`
                    $outboundContainer.append(acl)
                }
            });
        } else {
            $outboundContainer.append(noneAssigned)
        }
    })
}

function showOtherInterfaceCmds() {
    const interfaces = document.querySelectorAll(".interface")
    const card = function(cmd) {
        return `<div class='card'>${cmd}<span class='remove command'>X</span></div>`
    }
    
    interfaces.forEach( interface => {
        const $int = $( interface )
        const interfaceTitle = $int.find(".interface-title").text().replace("/", "\\/")
        const otherCmds = $int.find(`#id_${interfaceTitle}-other_commands`).val()  
        const container = $int.find(`#${interfaceTitle}-other-cmds`)
        otherCmds.split(",").forEach( cmd => {
            if (cmd) container.append(card(cmd))
        })
    })
}

function dropdown(id) {
    const section = document.querySelector(`[int-number="${id}"]`);
    const dropdownBottom = section.querySelector(".dropdown-bottom");
    const arrow = section.querySelector(".arrow");

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
    const termURI = document.location.href + "term";
    const csrfToken = $( 'input[name=csrfmiddlewaretoken]' ).val();
    const termPrompt = "";
    const error = false;

    const intro = [
        "LANwhiz CLI Interface",
        "\nUse for constious 'show' commands and other bespoke configuration",
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
                    for (const i in response) term.writeln(response[i]);
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
    showOtherInterfaceCmds()
    showACLCards();
    displayTerminal();
    showGlobalCmds();
    displayConfigSection("access");
});