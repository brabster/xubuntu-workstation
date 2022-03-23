Not intended for general use.

## Usage

```
sudo apt install git ansible &&
  mkdir -p ~/projects/brabster &&
  cd ~/projects/brabster &&
  git clone https://github.com/brabster/xubuntu-workstation.git &&
  cd ~/projects/xubuntu-workstation
    ansible-galaxy install -r requirements.yml &&
    ansible-playbook -vv workstation.yml &&
    git remote rm origin &&
    git remote add origin git@github.com:brabster/xubuntu-workstation.git
```

## Post-Install

- `cat ~/Downloads/eicar.com` (should fail with permissions issue)
- `cat ~/.ssh/id_ssh.pub` Add new SSH key to Github, remove old key
- `expressvpn activate`, `expressvpn autoconnect true`
- Log into LastPass, set autofill to false

