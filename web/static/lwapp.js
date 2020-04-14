const newDropdown = function(name, form, dropdownType="") {
    return `
    <div class="dropdown">
        <h5 class="dropdown-title">${name}<span style="float: right; padding-right:15px;"><i class="arrow down"></span></i></h5>
        <div class="dropdown-bottom">
            <div class="input-fields">
                <table class="form-table">
                    <tbody>
                        ${form}
                    </tbody>
                </table>
            </div>
            <button class="button1 remove-${dropdownType}" style="margin: 5">Remove</button>
        </div>
    </div>`
}

const newCard = function(text, name="") {
    return `<div style='margin-right: 10px;' class='card ${name}'>${text}<span class="remove ${name}">&times;</span></div>`
}



function displayConfigSection(sectionClass) {
    $(".config-inputs").hide()
    $(`.config-inputs.${sectionClass}`).fadeIn()
}

function showGlobalCmds() {
    var container = $("#globalCmdsContainer")
    var cmds = $("#globalCmds").val().split(",")

    cmds.forEach(function(cmd) {
        if (cmd) container.append(newCard(cmd))
    })

    $(".global-commands").on("click", ".card .remove", function() {
        var hidden = $("#globalCmds")
        var cmds = hidden.val() ? hidden.val().split(",") : []
        var cardToRemove = $(this).parent()
        var cmdToRemove = cardToRemove.text().slice(0, -1);
        hidden.val(cmds.filter(e => e !== cmdToRemove).join(","))
        cardToRemove.remove()
    })

    $("#addCmd").on("click", function(e) {
        e.preventDefault()
        var newCmd = $("#newCmd")
        if (!newCmd.val()) return

        var hidden = $("#globalCmds")
        var cmds = hidden.val() ? hidden.val().split(",") : []
        cmds.push(newCmd.val())

        $("#globalCmdsContainer").append(newCard(newCmd.val()))
        newCmd.val("")
        hidden.val(cmds.join(","))
    })
}

function showACLCards() {
    var interfaces = document.querySelectorAll(".interface, .line")

    interfaces.forEach(interface => {
        var $int = $(interface)
        var interfaceTitle = $int.find(".dropdown-title").text().replace("/", "\\/")
        var $inboundContainer = $int.find(`#${interfaceTitle}-inbound-container`)
        var $outboundContainer = $int.find(`#${interfaceTitle}-outbound-container`)
        var inboundACLs = $int.find(`#id_${interfaceTitle}-inbound_acl`).val()
        var outboundACLs = $int.find(`#id_${interfaceTitle}-outbound_acl`).val()
        const aclCard = function(direction, acl) {
            return `<div style='margin-right: 10px;' class='card acl ${direction}'>${acl}<span class="remove acl">&times;</span></div>`
        }

        if (inboundACLs) {
            inboundACLs.split(",").forEach(acl => {
                if (acl) $inboundContainer.append(aclCard("in", acl))
            })
        }

        if (outboundACLs) {
            outboundACLs.split(",").forEach(acl => {
                if (acl) $outboundContainer.append(aclCard("out", acl))
            })
        }
    })

    $(".dropdown div[id$=-acl]").on("click", ".card.acl .remove.acl", function() {
        console.log(this)
        const intDropdown  = $( this ).closest("div[class*=dropdown]")
        const cardClass    = $( this ).parent().attr("class")
        const direction    = cardClass.includes("in") ? "inbound" : "outbound"
        const hidden       = intDropdown.find(`input[id$=${direction}_acl]`)
        const cmds         = hidden.val() ? hidden.val().split(",") : []
        const cardToRemove = $( this ).parent()
        const cmdToRemove  = cardToRemove.text().slice(0, -1)

        hidden.val(cmds.filter(e => e !== cmdToRemove).join(","))
        cardToRemove.remove()
    })

    $( ".button1.assign-acl" ).on("click", function(e) {
        e.preventDefault()
        const aclName = $( this ).parent().find("select").find(":selected").text()
        const direction = $( this ).parent().find("input[name=acl-direction]:checked").val()

        if (!direction) {
            alert("Inbound or Outbound?")
            return
        }

        const aclInput = $(this).parent().parent().find(`[id*=${direction}_acl]`)
        const allAcls = aclInput.val() ? aclInput.val().split(",") : []
        
        if (!allAcls.includes(aclName)) {
            const cardName = direction === "inbound" ? "acl in" : "acl out"
            allAcls.push(aclName)
            aclInput.val(allAcls.join(","))
            $( this ).siblings( `[id*=${direction}-container]` ).append(newCard(aclName, cardName))
        }

    })
}

function showOtherInterfaceCmds() {
    var interfaces = document.querySelectorAll(".interface, .line")

    interfaces.forEach(interface => {
        if (interface) {
            var $int = $( interface )
            var interfaceTitle = $int.find(".dropdown-title").text().replace("/", "\\/")
            var otherCmds = $int.find(`#id_${interfaceTitle}-other_commands`).val()
            var container = $int.find(`#${interfaceTitle}-other-cmds`)

            if (otherCmds) otherCmds.split(",").forEach(cmd => {
                if (cmd) container.append(newCard(cmd))
            })
        }
    })

    $("button[id$=addOtherCmd]").on("click", function(e) {
        e.preventDefault()
        var newCmdInput = $(this).parent().find("input")
        var intDropdown = $(this).closest("div[class*=dropdown]")
        var hidden = intDropdown.find("input[id$=other_commands]")

        if (!newCmdInput.val()) return

        var cmds = hidden.val() ? hidden.val().split(",") : []
        cmds.push(newCmdInput.val())

        $($(this).parent()).append(newCard(newCmdInput.val()))
        newCmdInput.val("")
        hidden.val(cmds.join(","))
    })

    $( "div[id$=-other-cmds]" ).on("click", ".card .remove", function() {
        var intDropdown = $(this).closest("div[class*=dropdown]")
        var hidden = intDropdown.find("input[id$=other_commands]")
        var cmds = hidden.val() ? hidden.val().split(",") : []
        var cardToRemove = $(this).parent()
        var cmdToRemove = cardToRemove.text().slice(0, -1)
        hidden.val(cmds.filter(e => e !== cmdToRemove).join(","))
        cardToRemove.remove()
    })
}

function dropdown(section) {
    var dropdownBottom = section.find(".dropdown-bottom")
    var arrow = section.find(".arrow")

    if (dropdownBottom.css("display") === "inline-flex") {
        $( arrow ).attr("class", "arrow down")
        $( dropdownBottom ).slideUp()
    } else {
        $( arrow ).attr("class", "arrow up")
        $( dropdownBottom ).slideDown()
        $( dropdownBottom ).css("display", "inline-flex")
    }
}

function refreshACLSelects() {
    var allACLSelects = $(".available-acls")
    var allACLs = $("#allACLs")
}

// function displayTerminal() {
//     const statusDot = $( ".status.dot" ) 
//     const term = new Terminal({
//         cursorBlink: true
//     })
//     const hostname = $( "h2" ).text().split(" ")[2]
//     term.open(document.getElementById('terminal'))
//     var termURI = document.location.href + "term"
//     var csrfToken = $('input[name=csrfmiddlewaretoken]').val()
//     var termPrompt = ""
//     var error = false

//     var intro = [
//         "LANwhiz CLI Interface",
//         "\nUse for various 'show' commands and other bespoke configuration",
//         "\nNOTE: Changing the config areas which are overseen by the program will",
//         "require a config sync once finished.\n",
//         "Connecting...\n"
//     ]
//     for (i in intro) term.writeln(intro[i])


//     $.ajax({
//         url: `/ajax/${hostname}/term`,
//         data: {
//             "cmd": cmd
//         }, 
//         datatype: "json",
//         success: response => {
//             if ('error' in response) {
//                 error = true
//                 term.writeln("Error: " + response.error)
//                 statusDot.css("background-color", "#ff0000")
//                 $( "#statusSpinner" ).hide()
//             } else {
//                 term.writeln("Connected!\n\n")
//                 termPrompt = response.prompt
//                 term.write(termPrompt)
//                 $( "#statusSpinner" ).hide()
//                 statusDot.css("background-color", "#00ff00")
//             }
//             statusDot.show()
//         }
//     })

//     cmd = ""

//     term.onKey(e => {
//         var printable = !e.domEvent.altKey && !e.domEvent.altGraphKey && !e.domEvent.ctrlKey && !e.domEvent.metaKey
//         if (!termPrompt || error) return

//         if (e.domEvent.keyCode === 13) {
//             if (cmd) {
//                 $.ajax({
//                     url: `/ajax/${hostname}/term`,
//                     data: {
//                         "cmd": cmd
//                     }, 
//                     datatype: "json",
//                     success: response => {
//                         console.log(response)
//                         termPrompt = response.prompt
//                         response = response.cmd_out
//                         term.writeln("")
//                         for (var i in response) term.writeln(response[i])
//                         cmd = ""
//                         term.write(termPrompt)
//                     }
//                 })
//             } else {
//                 term.write("\n" + "\b".repeat(term._core.buffer.x) + termPrompt)
//             }
//         } else if (e.domEvent.keyCode === 8) {
//             // Do not delete the prompt
//             if (term._core.buffer.x > termPrompt.length) {
//                 term.write('\b \b')
//                 cmd = cmd.slice(NaN, -1)
//             }
//         } else if (printable) {
//             term.write(e.key)
//             cmd += e.key
//         }
//     })
// }

function displayTerminal() {
    term = new Terminal({
        cursorBlink: true
    })
    const statusDot = $( ".status.dot" ) 
    term.open(document.getElementById('terminal'));
    const hostname = $( "h2" ).text().split(" ")[2]
    var termURI = `/ajax/${hostname}/term`
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

    cmd = "";

    $.ajax({
        url: `/ajax/${hostname}/term`,
        data: {
            "connect": 1
        }, 
        datatype: "json",
        success: response => {
            if ('error' in response) {
                error = true
                term.writeln("Error: " + response.error)
                statusDot.css("background-color", "#ff0000")
                $( "#statusSpinner" ).hide()
            } else {
                term.writeln("Connected!\n\n")
                termPrompt = response.prompt
                term.write(termPrompt)
                $( "#statusSpinner" ).hide()
                statusDot.css("background-color", "#00ff00")
            }
            statusDot.show()
        }
    })

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
        return `
        <div style="width: 300; margin: 10" class="input-fields static-route">
            <span style="float: right; padding: 0;" class="remove command">&times;</span>
            <p><b>Destination Network:</b> ${net}</p>
            <p><b>Subnet Mask:</b> ${sm}</p>
            <p><b>Forward to:</b> ${to}</p>
        </div>`
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
        routeToRemove.map( (route, i) => {
            routeToRemove[i] = route.split(/\s+/)[0]
        })
        const currentRoutes = $routesInput.val() ? $routesInput.val().split(",") : []
        $routesInput.val(currentRoutes.filter(e => e !== routeToRemove.join("-")).join(","))
        card.remove()
    })

    $( "[name=forward-type]" ).change( function() {
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
        const currentRoutes = $routesInput.val() ? $routesInput.val().split(",") : []
        var forwardTo = null

        if ($("[name=forward-type]:checked").val() === "interface") {
            forwardTo = $( "#forwardInterfaces" ).find(":selected").text()
        } else {
            forwardTo = $( "#forwardNetwork" ).val()
        }

        if ( !(destNetwork && subnetMask && forwardTo) ) {
            alert("Destination, Subnet mask or forward network/interface missing!")
            return
        }
        
        const route = [destNetwork, subnetMask, forwardTo].join("-")

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
        return `
        <div style='margin-right: 10px;' value="${text}" class='card ${name}'><span class="remove">&times;</span>${text}</div>`
    }
    if (!$nets.val()) return
    $nets.val().split(",").forEach( net => {
        console.log(net)
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

        if (newValue.includes(`${net}/area ${area}`)) {
            alert("Already exists!")
            return
        }

        if (newValue.length >= 24) {
            alert("24 Networks allowed!")
            return
        }
        
        newValue.push(`${net}/area ${area}`)
        $nets.val(newValue.join(","))
        $( ".networks-container" ).append( card( "network", `<p>${net}</p><br><p>Area: ${area}</p>` ) )

    })

    $( ".networks-container" ).on("click", ".card .remove", function() {
        const netsInput = $( "#id_advertise_networks" )
        var net = $( this ).parent().text()

        netToRemove = net.replace("Area:", "/area").split(/\s+/).slice(2, 4).join(" ")
        currentNets = netsInput.val().split(",")
        $nets.val(currentNets.filter(e => e !== netToRemove).join(","))
        $( this ).parent().remove()
    })

    $( "#addPassiveInt" ).on("click", function(e) {
        e.preventDefault()
        const interface = $( "#passiveInterfaces" ).find(":selected").text()
        const inputValue = $passiveInts.val() ? $passiveInts.val().split(",") : []

        if (!inputValue.includes(interface)) {
            inputValue.push(interface)
            $passiveInts.val(inputValue.join(","))
            $( ".passive-ints-container" ).append( card( "passive-interface", `<p>${interface}</p>` ) )
        }
    })

    $( ".passive-ints-container" ).on("click", ".card .remove", function() {
        const interface = $( this ).parent().text().split(/\s+/).slice(2, 3)[0]
        const inputValue = $passiveInts.val().split(",")
        $passiveInts.val(inputValue.filter(e => e !== interface).join(","))
        $( this ).parent().remove()
    })

    $( "#addOSPFOtherCmd" ).on("click", e => {
        e.preventDefault()
        const newCmd = $( "#OSPFOtherCmd" ).val()
        const inputValue = $otherCmds.val() ? $otherCmds.val().split(",") : []

        if (!inputValue.includes(newCmd) && newCmd) {
            inputValue.push(newCmd)
            $otherCmds.val(inputValue.join(","))
            $( ".other-cmds-container" ).append( card( "other-cmd", `<p>${newCmd}</p>` ) )
            $( "#OSPFOtherCmd" ).val("")
        }
    })

    $( ".other-cmds-container" ).on("click", ".card.other-cmd .remove", function() {
        const cmd = $( this ).parent().text().slice(1)
        const inputValue = $otherCmds.val() ? $otherCmds.val().split(",") : []
        $otherCmds.val(inputValue.filter(e => e !== cmd).join(","))
        $( this ).parent().remove()
    })
}

function newRoutingProtocolInit() {
    const hostname = $( "h2" ).text().split(" ")[2]

    $( "#newRoutingProtocol" ).on("click", function(e) {
        e.preventDefault()
        const protocol = $( "#routingProtocol" ).find(":selected").text()
        
        if (!$( ".dynamic-routes" ).children().text().includes(protocol)) {
            $.ajax({
                url: "/ajax/new-routing-protocol",
                data: {
                    "hostname": hostname,
                    "protocol": protocol
                },
                datatype: "json",
                success: response => {
                    $( ".dynamic-routes" ).append(newDropdown(protocol, response.form, "routing-protocol"))
                }
            })
        }
    })
}

function overlayInit() {
    const overlay = $( "#overlay" ) 
    const box = $( ".box" )
    const boxInner = $( "#boxInner" )
    const hostname = $( "h2" ).text().split(" ")[2]
    const savedNotification = $(".changes-saved-notification")
    const newChange = function(name, value) {
        return `
        <div class="changes">
            <h5><b>${name}:</b> ${value}</h5>
        </div>`
    }

    $( ".diff-config" ).on("click", e => {
        e.preventDefault()
        $.ajax({
            type: "POST",
            url: `/devices/${hostname}/diff-config`,
            data: $( "#deviceConfig" ).serialize(),
            success: resp => {
                if (!resp.changed.length) {
                    alert("No changes have been made")
                    return
                }
                boxInner.html("")
                resp.changed.forEach(area => {
                    boxInner.append(`<h5 class="dropdown-title" style="font-size: 19">${area}</h5>`)
                })
                overlay.fadeIn()
                box.fadeIn()
            }
        })
    })

    $( ".confirm-changes" ).on("click", e => {
        e.preventDefault()
        $.ajax({
            type: "POST",
            url: `/devices/${hostname}/diff-config?save=1`,
            data: $( "#deviceConfig" ).serialize(),
            success: resp => {
                if (resp.saved) {
                    $( "#lastModifiedTimestamp" ).text(`Last modified: ${resp.time_updated}`)
                }
                else {
                    alert("Error occured while saving config")
                    return
                }

            }
        })
        overlay.fadeOut()
        box.fadeOut()
        $( document ).scrollTop(0)
        savedNotification.show()
        savedNotification.fadeOut(5000)
    })

    overlay.on("click", () => {
        overlay.fadeOut()
        box.fadeOut()
    })
}


function ACLInit() {
    const hostname = $( "h2" ).text().split(" ")[2]
    const refreshACLSelects = () => {
        const selects = $( ".available-acls" )
        selects.html("")
    
        $( ".config-inputs.acl" ).find("h5").map( (_, aclName) => {
            const acl = $( aclName ).text()
            selects.append(`<option>${acl}</option>`)
        })
    }

    refreshACLSelects()

    $( "#addACL" ).on("click", e => {
        e.preventDefault()
        const aclName = $( "#newACL" ).val()
        const aclType = $( "[name=acl-type]:checked" ).val()
        const hostname = $( "h2" ).text().split(" ")[2]


        if (!(aclName && aclType)) {
            alert("Name and type must be specified!")
            return
        } 

        if (parseInt(aclName)) {
            const aclNum = parseInt(aclName)
            if ((aclType === "standard" && !(1 <= aclNum && aclNum <= 100)) || 
                (aclType === "extended" && !(101 <= aclNum && aclNum <= 200))) {
                alert("ACL number out of range!")
                return
            }
        } else if (aclName.match(/\s/)) {
            alert("Names cannot contain spaces!")
            return
        }
        
        $.ajax({
            url: "/ajax/new-acl",
            data: {
                "hostname": hostname,
                "acl_type": aclType,
                "acl_name": aclName
            },
            datatype: "json",
            success: response => {
                $( `#${response.acl_type}ACLs` ).append(newDropdown(aclName, response.form, `acl ${aclType}`))
                refreshACLSelects()
            }
        })
    })

    $(".remove-acl").on("click", function(e) {
        e.preventDefault()
        const aclType = this.className.split(" ")[2]
        const aclName = $( this ).parent().parent().find(".dropdown-title").text()

        $.ajax({
            url: "/ajax/remove-acl",
            data: {
                "hostname": hostname,
                "acl_type": aclType,
                "acl_name": aclName
            },
            datatype: "json",
            success: response => {
                if (response.removed) {
                    $(`h5:contains('${aclName}')`).parent().remove()
                    refreshACLSelects()
                }
            }
        })
    })
}
 
function newDHCPPoolInit() {
    const hostname = $( "h2" ).text().split(" ")[2]
    $( "#addDHCP" ).on("click", e => {
        e.preventDefault()
        const poolName = $( "#newDHCP" ).val()
        
        if (!poolName) {
            alert("Pool name not specified!")
            return
        } else if (poolName.match(/\s/)) {
            alert("Names cannot contain spaces!")
            return
        }

        $.ajax({
            url: "/ajax/dhcp-pool",
            data: {
                "hostname": hostname,
                "pool_name": poolName
            },
            datatype: "json",
            success: response => {
                $( "#DHCPPoolsContainer" ).append(newDropdown(poolName, response.form, "dhcp-pool"))
            }
        })
    })

    $( "#DHCPPoolsContainer" ).on("click", ".remove-dhcp-pool", function(e) {
        e.preventDefault()
        const poolName = $( this ).parent().siblings(".dropdown-title").text()
        $.ajax({
            url: "/ajax/dhcp-pool",
            data: {
                "action": "remove",
                "hostname": hostname,
                "pool_name": poolName
            },
            datatype: "json",
            success: response => {
                $( this ).parent().parent().remove()
            }
        })
    })
}

function newLoopbackInterfaceInit() {
    $( "#addLoopback" ).on("click", function(e) {
        e.preventDefault()
        const hostname = $( "h2" ).text().split(" ")[2]
        const intNumber = $( "#loopbackNumber" ).val()
        const container = $( ".interfaces" )

        if (!intNumber) {
            alert("Specify Interface Number!")
            return
        } else if (!intNumber.match(/^\d{1,3}$/)) {
            alert("Maximum of 3 digits only!")
            return
        }
        
        $.ajax({
            url: "/ajax/new-loopback-interface",
            data: {
                "hostname": hostname,
                "number": intNumber
            },
             datatype: "json",
             success: response => {
                $( ".interfaces" ).append(newDropdown(`Loopback${intNumber}`, response.form, "interface"))
             }
        })
    })
}


$( document ).ready( () => {
    overlayInit()
    showDynamicRoutingCards()
    showStaticRoutingCards()
    showACLCards()
    showGlobalCmds()
    displayTerminal()
    showOtherInterfaceCmds()
    newLoopbackInterfaceInit()
    ACLInit()
    newDHCPPoolInit()
    newRoutingProtocolInit()
    displayConfigSection("access")
})