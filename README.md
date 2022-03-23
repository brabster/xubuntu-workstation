Ubuntu 20.04

## Usage

```
sudo apt install git ansible &&
  mkdir -p ~/projects/brabster &&
  cd ~/projects/brabster &&
  git clone https://github.com/brabster/ubuntu-workstation.git &&
  cd ~/projects/ubuntu-workstation



    ansible-galaxy install -r requirements.yml &&
    ansible-playbook -vv workstation.yml &&
    git remote rm origin &&
    git remote add origin git@github.com:brabster/workstation-setup.git
```

## Post-Install

- `cat ~/Downloads/eicar.com` (should fail with permissions issue)
- `cat ~/.ssh/id_ssh.pub` Add new SSH key to Github, remove old key
- `expressvpn activate`, `expressvpn autoconnect true`
- Log into LastPass, set autofill to false

