#!/bin/bash

PACKAGES=(
    "git"
    "hyprpaper"
    "hypridle"
    "neovim"
    "htop"
    "python-fabric-git"
    "yazi"
    "zellij"
    "haruna"
    "flameshot-git"
    "zen-browser"
    "obs-studio"
    "krita"
    "obsidian"
    "tahoma2d"
    "libreoffice-fresh"
    "neofetch"
    "auto-cpufreq"
    "virtualbox"
    "wine-staging-git"
    "wine-valve"
    "winegui-bin"
    "winetricks"
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
    "megacubo-bin"
    "megasync"
    "cava"
    "heroic-games-launcher-bin"
    "acpi"
    "rustup"
    "edex-ui"
    "zsh-autosuggestions"
    "antigen"
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
    
    read -p "Do you want to let us install everything for you or confirm what to install (some of these are necessary for certain functionalities)? [y/n]" confirm_ornot
    if [ "$confirm_ornot" == "y" ]; then
        
        echo "Installing packages..."
        for pkg in "${PACKAGES[@]}"; do
            if yay -Qi "$pkg" >/dev/null 2>&1; then
                echo "Package '$pkg' is already installed."
            else
                read -p "Should we proceed with installing '$pkg' ? (y/n)" install_choice
                if [ "$install_choice" == "y" ]; then
                    echo "Installing '$pkg'..."
                    yay -S --noconfirm "$pkg"
                else
                    echo "Skipping '$pkg'"
                fi
            fi
        done
    else
        echo "Installing packages..."
        for pkg in "${PACKAGES[@]}"; do
            if yay -Qi "$pkg" >/dev/null 2>&1; then
                echo "Package '$pkg' is already installed."
            else
                read -p "Should we proceed with installing '$pkg' ? (y/n)" install_choice
                if [ "$install_choice" == "y" ]; then
                    echo "Installing '$pkg'..."
                    yay -S --noconfirm "$pkg"
                else
                    echo "Skipping '$pkg'"
                fi
            fi
        done
    fi 

    echo "All done!"
}

main
