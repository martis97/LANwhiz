
$VerbosePreference = "Continue"

function Install-LANwhiz {

    #section Python Version
    Write-Verbose -Message  "Checking Python version.."
    $pythonVersion = (python --version).split(" ")[1]

    if (!$pythonVersion -match "^3") {
        Write-Verbose -Message  "Python 3 Required!"
        exit 1
    }
    #endsection Python Version


    #section Python Libs
    Write-Verbose -Message  "Installing Required Python libraries.."
    @("napalm", "django", "netmiko") | ForEach-Object {
        Write-Verbose "Installing $_ .."
        pip install $_
    }
    #endsection Python Libs

    #section PYTHONPATH
    $parentPath = (get-location).path -replace "LANwhiz", ""
    $currentPaths = $env:PYTHONPATH.split(";")

    if (!$currentPaths.contains($parentPath)) {
        Write-Verbose -Message "Adding Parent Directory to PYTHONPATH.."
        $env:PYTHONPATH = "$env:PYTHONPATH" + "$parentPath;"
    }
    #section PYTHONPATH

    Write-Verbose -Message "Happy Automating!"
}

Install-LANwhiz
