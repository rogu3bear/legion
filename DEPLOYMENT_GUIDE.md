# Deployment Guide: Rsync + Nginx

**To deploy via rsync, you need two setups: on the server and on your local machine.**

---

## 1. Server-Side Setup

1.  **Create a deploy user**

    ```bash
    sudo adduser deploy
    sudo usermod -aG www-data deploy
    ```

    *   "deploy" is just a suggestion. Pick a name your team prefers.

2.  **Install SSH keys**

    *   On your local machine, copy your public key:

        ```bash
        cat ~/.ssh/id_rsa.pub
        ```
    *   On the server, as root or via sudo:

        ```bash
        mkdir -p /home/deploy/.ssh
        echo "<PASTE_PUBLIC_KEY>" >> /home/deploy/.ssh/authorized_keys
        chmod 700 /home/deploy/.ssh
        chmod 600 /home/deploy/.ssh/authorized_keys
        chown -R deploy:deploy /home/deploy/.ssh
        ```

3.  **Prepare the web directory**

    ```bash
    sudo mkdir -p /var/www/auchsight
    sudo chown -R deploy:www-data /var/www/auchsight
    sudo chmod -R 755 /var/www/auchsight
    ```

4.  **Configure Nginx** (example `/etc/nginx/sites-available/auchsight`)

    ```nginx
    server {
      listen 80;
      server_name auchsight.com www.auchsight.com;
      root /var/www/auchsight;

      index index.html index.htm;
      location / {
        try_files $uri $uri/ =404;
      }
    }
    ```

    *   Enable it and reload Nginx:

        ```bash
        sudo ln -s /etc/nginx/sites-available/auchsight /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl reload nginx
        ```

---

## 2. Local-Side Setup

1.  **Ensure your SSH key is loaded**

    ```bash
    ssh-add ~/.ssh/id_rsa
    ```

2.  **Build the frontend**

    ```bash
    npm run build
    ```

3.  **Run the rsync command**

    ```bash
    rsync -avz build/ deploy@prod.auchsight.com:/var/www/auchsight
    ```

    *   Replace `deploy@prod.auchsight.com` with your chosen user@host.

4.  **Verify on the server**

    ```bash
    ssh deploy@prod.auchsight.com
    ls /var/www/auchsight
    ```

---

With those steps completed, your new build will be live on `auchsight.com`. 