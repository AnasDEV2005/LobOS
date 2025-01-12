#!/bin/bash

PACKAGES=(
    "hyprpaper"
    "hypridle"
    "neovim"
    "htop"
    "python-fabric-git"
    "yazi"
    "qview"
    "zellij"
    "haruna"
    "vesktop"
    "flameshot-git"
    "obs-studio"
    "krita"
    "obsidian"
    "libreoffice-fresh"
    "neofetch"
    "auto-cpufreq"
    "virtualbox"
    "lsd"
    "pacseek"
    "gtk3"
    "cairo"
    "gtk-layer-shell"
    "libgirepository"
    "gobject-introspection"
    "gobject-introspection-runtime"
    "python"
    "python-pip"
    "python-gobject"
    "python-cairo"
    "python-loguru"
    "pkgconf"
    "cava"
    "acpi"
    "rustup"
    "zsh-autosuggestions"
    "antigen"
    "zsh"
    "thunar"
    "meson"
    "python-pywayland"
    "vala"
    "gtk-session-lock"
    "zsh-autosuggestions"
    "figlet"
    "bat"
    "gdu"
    "bpytop"
    "htop"
    "ttf-unifont"
    "wayvibes-git"
    "alacritty"
    "dhcpcd"
    "swww-git"
    # Add more packages here
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
