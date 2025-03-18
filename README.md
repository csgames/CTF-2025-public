# CTF

Directeurs de compétition: Alexandre Aubut et Alexandre Lavoie

## Infrastructure

### Requirements

- [Docker](https://docs.docker.com/get-started/get-docker/)
    - For Linux, make sure [your user is part of the docker group](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
- [Python](https://www.python.org/)
    - [ctf-builder](https://pypi.org/project/ctf-builder/)

### Challenges

```bash
ctf build
ctf docker start
```

### CTFd

```bash
ctf ctfd dev
```

Default credentials are username `admin` and password `admin`.
