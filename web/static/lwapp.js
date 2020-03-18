function displayConfigSection(sectionClass) {
    var configInputs = document.querySelectorAll(".config-inputs");
    $(".config-inputs").hide()
    $(`.config-inputs.${sectionClass}`).fadeIn()
}

function showGlobalCmds() {
    var container = $("#globalCmdsContainer")
    var cmds = $("#globalCmds").val().split(",")

    cmds.forEach(function(cmd) {
        container.append(`<div style='margin-right: 10px;' class='card'>${cmd}<span class="remove command">&times;</span></div>`)
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
    var interfaces = document.querySelectorAll(".interface,.line")

    interfaces.forEach(interface => {
        var $int = $(interface)
        var interfaceTitle = $int.find(".dropdown-title").text().replace("/", "\\/")
        var $inboundContainer = $int.find(`#${interfaceTitle}-inbound-container`)
        var $outboundContainer = $int.find(`#${interfaceTitle}-outbound-container`)
        var inboundACLs = $int.find(`#id_${interfaceTitle}-inbound_acl`).val()
        var outboundACLs = $int.find(`#id_${interfaceTitle}-outbound_acl`).val()
        const card = function(direction, acl) {
            return `<div style='margin-right: 10px;' class='card acl ${direction}'>${acl}<span class="remove acl">&times;</span></div>`
        }

        if (inboundACLs) {
            inboundACLs.split(",").forEach(acl => {
                if (acl) $inboundContainer.append(card("in", acl))
            });
        }

        if (outboundACLs) {
            outboundACLs.split(",").forEach(acl => {
                if (acl) $inboundContainer.append(card("in", acl))
            });
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

            if (otherCmds) otherCmds.split(",").forEach(cmd => {
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


function showStaticRoutingCards() {
    const staticRoute = function(net, sm, to) {
        var cardText = '<div style="width: 300; margin: 10" class="input-fields static-route">'
        cardText += '<span style="float: right; padding: 0;" class="remove command">&times;</span>'
        cardText += `<p><b>Destination Network:</b> ${net}</p>`
        cardText += `<p><b>Subnet Mask:</b> ${sm}</p>`
        cardText += `<p><b>Forward to:</b> ${to}</p>`
        cardText += "</div>"

        return cardText
    }

    const $routesInput = $( "#staticRoutes" )
    var allRoutes = $routesInput.val()

    allRoutes.split(",").forEach( route => {
        if (route) {
            const [net, sm, to] = route.split("-")
            $( ".static-routes" ).append(staticRoute(net, sm, to))
        }
    })

    $( ".static-routes" ).on("click", ".input-fields.static-route .remove", function() {
        const card = $( this ).parent()
        const routeToRemove = card.text().split(/Destination Network: |Subnet Mask: |Forward to: /).slice(1)
        const currentRoutes = $routesInput.val() ? $routesInput.val().split(",") : []
        $routesInput.val(currentRoutes.filter(e => e !== routeToRemove.join("-")).join(","))
        card.hide()
    })

    $( "[name=forward-type]" ).change(function() {
        const $interfacesSelect = $( "#forwardInterfaces" )
        const $networkInput = $( "#forwardNetwork" )

        if ( this.value === "interface" ) {
            $interfacesSelect.show()
            $networkInput.hide()
        } else {
            $interfacesSelect.hide()
            $networkInput.show()
        }
    })

    $( "#addStaticRoute" ).on("click", function(e) {
        e.preventDefault()
        const destNetwork = $( "#id_network" ).val()
        const subnetMask = $( "#id_subnet_mask" ).val()
        var forwardTo = ""
        const currentRoutes = $routesInput.val() ? $routesInput.val().split(",") : []

        if ($("[name=forward-type]:checked").val() === "interface") {
            forwardTo = $( "#forwardInterfaces" ).find(":selected").text()
        } else {
            forwardTo = $( "#forwardNetwork" ).val()
        }

        if ( !destNetwork && !subnetMask && !forwardTo ) {
            alert("Destination, Subnet mask or forward network/interface missing!")
            return
        }
        
        const route = `${destNetwork}-${subnetMask}-${forwardTo}`

        if (!currentRoutes.includes(route)) {
            $( ".static-routes" ).append(staticRoute(destNetwork, subnetMask, forwardTo))
            currentRoutes.push(route)
            $routesInput.val(currentRoutes.join(","))
        }
        
    })

}


function showDynamicRoutingCards() {
    const $nets = $( "#id_advertise_networks" )
    const $passiveInts = $( "#id_passive_interfaces" )
    const $otherCmds = $( "#id_other_commands" )
    const card = function(name, text) {
        return `<div style='margin-right: 10px;' class='card ${name}'><span class="remove">&times;</span>${text}</div>`;
    }

    $nets.val().split(",").forEach( net => {
        var netInfo = net.split("/")
        var area = netInfo[2].match(/\d+/g)[0]
        var cardText = `<p>${netInfo[0]}/${netInfo[1]}</p><br><p>Area: ${area}</p>`
        $( ".networks-container" ).append( card( "network", cardText ) )
    } )

    $passiveInts.val().split(",").forEach( interface => {
        if (interface) $( ".passive-ints-container" ).append( card( "passive-interface", `<p>${interface}</p>` ) )
    } )
 
    $otherCmds.val().split(",").forEach( cmd => {
        if (cmd) $( ".other-cmds-container" ).append( card( "other-cmd", `<p>${cmd}</p>` ) )
    } )

    $( "#addOSPFNetwork" ).on("click", function(e) {
        e.preventDefault()
        const area = $( "[value=area0]" ).is(":checked") ? 0 : $( "#otherOspfArea" ).val()

        if (area === "") {
            alert("Please specify the area number!")
            return
        }

        const net = $( ".available-networks" ).find(":selected").text()
        const newValue = $nets.val() ? $nets.val().split(",") : []

        newValue.push(`${net}/area ${area}`)

        $( ".networks-container" ).append(card("network", `<p>${net}</p><br><p>Area: ${area}</p>`))

        $nets.val(newValue.join(","))
    })

    $( ".networks-container" ).on("click", ".card .remove", function() {
        const netsInput = $( "#id_advertise_networks" )
        var net = $( this ).parent().text()

        netToRemove = net.slice(1).replace("Area:", "/area")
        currentNets = netsInput.val().split(",")
        $nets.val(currentNets.filter(e => e !== netToRemove).join(","))
        $( this ).parent().hide()
    })

    $( "#addPassiveInt" ).on("click", function(e) {
        e.preventDefault()
        const interface = $( "#passiveInterfaces" ).find(":selected").text()
        const inputValue = $passiveInts.val() ? $passiveInts.val().split(",") : []

        if (!inputValue.includes(interface)) {
            inputValue.push(interface)
            $passiveInts.val(inputValue.join(","))
            $( ".passive-ints-container" ).append(card("passive-interface", `<p>${interface}</p>`))
        }
    })

    $( ".passive-ints-container" ).on("click", ".card .remove", function() {
        const interface = $( this ).parent().text().slice(1)
        const inputValue = $passiveInts.val() ? $passiveInts.val().split(",") : []
        $passiveInts.val(inputValue.filter(e => e !== interface).join(","))
        $( this ).parent().hide()
    })

    $( "#addOSPFOtherCmd" ).on("click", function(e) {
        e.preventDefault()
        const newCmd = $( "#OSPFOtherCmd" ).val()
        const inputValue = $otherCmds.val() ? $otherCmds.val().split(",") : []

        if (!inputValue.includes(newCmd) && newCmd) {
            inputValue.push(newCmd)
            $otherCmds.val(inputValue.join(","))
            $( ".other-cmds-container" ).append(card("other-cmd", `<p>${newCmd}</p>`))
            $( "#OSPFOtherCmd" ).val("")
        }
    })

    $( ".other-cmds-container" ).on("click", ".card .remove", function() {
        const cmd = $( this ).parent().text().slice(1)
        const inputValue = $otherCmds.val() ? $otherCmds.val().split(",") : []
        $otherCmds.val(inputValue.filter(e => e !== cmd).join(","))
        $( this ).parent().hide()
    })
}

$(document).ready(function() {
    showDynamicRoutingCards()
    showStaticRoutingCards()
    showACLCards()
    showGlobalCmds()
    displayTerminal()
    showOtherInterfaceCmds()
    displayConfigSection("access")
});