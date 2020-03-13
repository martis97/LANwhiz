function displayConfigSection(sectionClass) {
    var configInputs = document.querySelectorAll(".config-inputs");
    $(".config-inputs").hide()
    $(`.config-inputs.${sectionClass}`).fadeIn()
}

function showGlobalCmds() {
    var container = document.querySelector("#globalCmdsContainer");
    var cmds = $("#globalCmds").val().split(",");

    cmds.forEach(function(cmd) {
        container.innerHTML += `<div style='margin-right: 10px;' class='card'>${cmd}<span class="remove command">&times;</span></div>`;
    })

    $(".global-commands").on("click", ".card .remove", function() {
        var hidden = $("#globalCmds");
        var cmds = hidden.val() ? hidden.val().split(",") : [];
        var cardToHide = $(this).parent();
        var cmdToRemove = cardToHide.text().slice(0, -1);;
        hidden.val(cmds.filter(e => e !== cmdToRemove).join(","));
        cardToHide.hide();
    });

    $("#addCmd").on("click", function(e) {
        e.preventDefault()
        var newCmd = $("#newCmd");
        if (!newCmd.val()) return

        const card = function(cmd) {
            return `<div style='margin-right: 10px;' class='card'>${cmd}<span class="remove command">&times;</span></div>`;
        }

        var hidden = $("#globalCmds");
        var cmds = hidden.val() ? hidden.val().split(",") : [];
        cmds.push(newCmd.val());

        $("#globalCmdsContainer").append(card(newCmd.val()));
        newCmd.val("");
        hidden.val(cmds.join(","));
    });
}

function showACLCards() {
    var noneAssigned = '<span style="font-size: 10px;">None Assigned</span>'
    var interfaces = document.querySelectorAll(".interface,.line")

    interfaces.forEach(interface => {
        var $int = $(interface)
        var interfaceTitle = $int.find(".dropdown-title").text().replace("/", "\\/")
        var $inboundContainer = $int.find(`#${interfaceTitle}-inbound-container`)
        var $outboundContainer = $int.find(`#${interfaceTitle}-outbound-container`)
        var inboundACLs = $int.find(`#id_${interfaceTitle}-inbound_acl`).val()
        var outboundACLs = $int.find(`#id_${interfaceTitle}-outbound_acl`).val()

        if (inboundACLs) {
            inboundACLs.split(",").forEach(acl => {
                if (acl) {
                    acl = `<div style='margin-right: 10px;' class='card acl in'>${acl}<span class="remove acl">&times;</span></div>`
                    $inboundContainer.append(acl)
                }
            });
        } else {
            $inboundContainer.append(noneAssigned)
        }

        if (outboundACLs) {
            outboundACLs.split(",").forEach(acl => {
                if (acl) {
                    acl = `<div style='margin-right: 10px;' class='card acl out'>${acl}<span class="remove acl">&times;</span></div>`
                    $outboundContainer.append(acl)
                }
            });
        } else {
            $outboundContainer.append(noneAssigned)
        }
    })

    $("div[id$=-acl]").on("click", ".card .remove", function() {
        var intDropdown = $(this).closest("div[class*=interface]")
        var cardClass = $(this).parent().attr("class")

        if (cardClass.includes("in")) {
            var hidden = intDropdown.find("input[id$=inbound_acl]")
        } else if (cardClass.includes("out")) {
            var hidden = intDropdown.find("input[id$=outbound_acl]")
        }

        var cmds = hidden.val().split(",");
        var cardToHide = $(this).parent();
        var cmdToRemove = cardToHide.text().slice(0 - 1);
        hidden.val(cmds.filter(e => e !== cmdToRemove).join(","));
        cardToHide.hide();

    });
}

function showOtherInterfaceCmds() {
    var interfaces = document.querySelectorAll(".interface")
    var card = function(cmd) {
        return `<div class='card'>${cmd}<span class='remove command'>&times;</span></div>`
    }

    interfaces.forEach(interface => {
        if (interface) {
            var $int = $(interface)
            var interfaceTitle = $int.find(".dropdown-title").text().replace("/", "\\/")
            var otherCmds = $int.find(`#id_${interfaceTitle}-other_commands`).val()
            var container = $int.find(`#${interfaceTitle}-other-cmds`)

            otherCmds.split(",").forEach(cmd => {
                if (cmd) container.append(card(cmd))
            })
        }
    })

    $("button[id$=addOtherCmd]").on("click", function(e) {
        e.preventDefault()
        var newCmdInput = $(this).parent().find("input")
        var intDropdown = $(this).closest("div[class*=interface]")
        var hidden = intDropdown.find("input[id$=other_commands]")

        if (!newCmdInput.val()) return

        const card = function(cmd) {
            return `<div style='margin-right: 10px;' class='card'>${cmd}<span class="remove command">&times;</span></div>`;
        }

        var cmds = hidden.val() ? hidden.val().split(",") : [];
        cmds.push(newCmdInput.val());

        $($(this).parent()).append(card(newCmdInput.val()));
        newCmdInput.val("");
        hidden.val(cmds.join(","));
    });

    $("div[id$=-other-cmds]").on("click", ".card .remove", function() {
        var intDropdown = $(this).closest("div[class*=interface]")
        var hidden = intDropdown.find("input[id$=other_commands]")
        var cmds = hidden.val() ? hidden.val().split(",") : [];
        var cardToHide = $(this).parent();
        var cmdToRemove = cardToHide.text().slice(0, -1);
        hidden.val(cmds.filter(e => e !== cmdToRemove).join(","));
        cardToHide.hide();
    });
}

function dropdown(section) {
    var dropdownBottom = section.find(".dropdown-bottom");
    var arrow = section.find(".arrow");

    if (dropdownBottom.css("display") === "inline-flex") {
        $(arrow).attr("class", "arrow down")
        $(dropdownBottom).slideUp(600);
    } else {
        $(arrow).attr("class", "arrow up")
        $(dropdownBottom).slideDown(600);
        $(dropdownBottom).css("display", "inline-flex")
    }
}

function refreshACLSelects() {
    var allACLSelects = $(".available-acls")
    var allACLs = $("#allACLs")
}

function displayTerminal() {
    term = new Terminal();
    term.open(document.getElementById('terminal'));
    var termURI = document.location.href + "term";
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
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
        var printable = !e.domEvent.altKey && !e.domEvent.altGraphKey && !e.domEvent.ctrlKey && !e.domEvent.metaKey;
        if (!termPrompt || error) return;

        if (e.domEvent.keyCode === 13) {
            if (cmd) {
                $.post(termURI, {
                    csrfmiddlewaretoken: csrfToken,
                    cmd: cmd
                }, response => {
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
                cmd = cmd.slice(NaN, -1)
            }
        } else if (printable) {
            term.write(e.key);
            cmd += e.key;
        }

    });

}


$(document).ready(function() {
    showACLCards()
    showGlobalCmds()
    displayTerminal()
    showOtherInterfaceCmds()
    displayConfigSection("access")
});