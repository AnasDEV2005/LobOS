#!/bin/bash


PACKAGES=(
    # "bartib"
    # "bat"
    # "bpytop"
    # "cava"
    "acpi"
    "alacritty"
    "antigen"
    "auto-cpufreq"
    "cairo"
    # "figlet"
    # "flameshot-git"
    # "freeter"
    # "gdu"
    "dhcpcd"
    "gobject-introspection"
    "gobject-introspection-runtime"
    "gtk-layer-shell"
    "gtk-session-lock"
    "gtk3"
    "hypridle"
    "libgirepository"
    "lsd"
    # "lutris"
    # "mission-center"
    "meson"
    "neofetch"
    "neovim"
    # "obs-studio"
    # "obsidian"
    # "pacseek"
    "pkgconf"
    "playerctl"
    "python"
    "python-cairo"
    "python-fabric-git"
    "python-gobject"
    "python-loguru"
    "python-pip"
    "python-pywayland"
    "swww"
    "thunar"
    "ttf-unifont"
    # "vala"
    # "vesktop"
    # "virtualbox"
    # "wayvibes-git"
    # "yazi"
    "zellij"
    "zsh"
    "zsh-autosuggestions"
    # "zen-browser"
    # "krita"
    # "htop"
    # "haruna"
    # "libreoffice-fresh"
)


command_exists() {
    command -v "$1" >/dev/null 2>&1
}

install_yay() {
    echo "Installing 'yay' (AUR helper)..."
    sudo pacman -S --needed --noconfirm base-devel git
    git clone https://aur.archlinux.org/yay.git
    cd yay || exit
    makepkg -si --noconfirm
    cd ..
    rm -rf yay
}

main() {
    if ! command_exists yay; then
        echo "'yay' is not installed. Installing..."
        install_yay
    else
        echo "'yay' is already installed."
    fi
    
        echo "Installing packages..."
        for pkg in "${PACKAGES[@]}"; do
            if yay -Qi "$pkg" >/dev/null 2>&1; then
                echo "Package '$pkg' is already installed."
            else
                echo "Installing '$pkg'..."
                yay -S $pkg --noconfirm

            fi
        done

    echo "All done!"
}

main 

# Enable and start daemons for installed packages

# System services
declare -A SYSTEM_SERVICES=(
    [auto-cpufreq]="auto-cpufreq"
    [dhcpcd]="dhcpcd"
    [virtualbox]="vboxservice"
)

# User (session) daemons
USER_DAEMONS=(
    "swww"
)

echo "🔍 Checking and enabling system daemons..."
for pkg in "${!SYSTEM_SERVICES[@]}"; do
    service="${SYSTEM_SERVICES[$pkg]}"

    if pacman -Qi "$pkg" &>/dev/null; then
        echo "✅ Found $pkg — enabling $service.service..."
        sudo systemctl enable "$service.service"
        sudo systemctl start "$service.service"
    else
        echo "⚠️  Package $pkg not installed, skipping system service."
    fi
done

echo
echo "👤 Starting user daemons..."
for daemon in "${USER_DAEMONS[@]}"; do
    if pacman -Qi "$daemon" &>/dev/null; then
        if ! pgrep -x "${daemon}-daemon" &>/dev/null; then
            echo "✅ Launching ${daemon}-daemon..."
            "${daemon}-daemon" &
        else
            echo "ℹ️  ${daemon}-daemon already running."
        fi
    else
        echo "⚠️  Package $daemon not installed, skipping user daemon."
    fi
done

echo
echo "🎉 Done! All relevant services and daemons are now active."
