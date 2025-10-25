#!/bin/bash



echo "This install script is mostly made for Arch Linux, or anything with a similar file structure"


sudo pacman -Syuu

sudo chown -R $USER:$USER ~/.config

if ! command -v hyprctl &> /dev/null; then
    echo "Hyprland is not installed. Installing Hyprland..."
    yay -S hyprland
else
    echo "Hyprland is already installed."
fi

echo "Starting install..."
echo "Proceeding to install packages and dependencies"
chmod +x ./arch-installations.sh
./arch-installations.sh




# curl -L -o Tahoma2D_1.5.2.AppImage \
     # https://github.com/tahoma2d/tahoma2d/releases/download/v1.5.2/Tahoma2D_1.5.2_amd64.AppImage





cd ~
cd .config/hypr
sudo rm -rf ./fabric-venv
mkdir fabric-venv
python -m venv fabric-venv
source fabric-venv/bin/activate
pip install git+https://github.com/Fabric-Development/fabric.git
pip install psutil
pip install loguru
pip install pynput

echo "Attempting to install libcvc"

git clone https://github.com/Fabric-Development/fabric.git

chmod +x ~/fabric/scripts/install_libcvc/install_libcvc.sh
~/fabric/scripts/install_libcvc/install_libcvc.sh


cd ~
git clone https://github.com/AnasDEV2005/my-scripts.git
cd my-scripts
sudo cp ./* /usr/local/bin


cd ~ 
touch fabric-notes.txt 


echo "installing dotfiles"

cd ~
git clone https://github.com/zsh-users/zsh-autosuggestions

sudo mv ~/LobOS/hypr/.zshrc ~/.zshrc

sudo cp -r ~/LobOS/hypr ~/.config

sudo cp -r ~/LobOS/alacritty ~/.config

sudo cp -r ~/LobOS/nvim ~/.config

sudo mv -r ~/LobOS/neofetch1 ~/.config/neofetch 

sudo cp -r ~/LobOS/themes ~/.config/vesktop

sudo rm /etc/sddm.conf.d
sudo mkdir /etc/sddm.conf.d/
sudo cp ~/LobOS/autologin.conf /etc/sddm.conf.d/

sudo cp -r ~/LobOS/newfont.ttf /usr/share/fonts

echo "Verifying python packages"

sudo chown -R $USER:$USER ~/.config
sudo chmod -R 700 ~/.config

python -m ensurepip --upgrade
source ~/.config/hypr/fabric-venv/bin/activate
cd ~/.config/hypr 
source ./fabric-venv/bin/activate
pip install loguru
pip install psutil
pip install subprocess
pip install pam







echo "3"
echo "2"
echo "1"
echo "Done!"


sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
