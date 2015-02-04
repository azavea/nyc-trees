# Applying Migrations

The following instructions can be used to apply migrations to an AWS stack of this project.

## Prerequisites

- Access to the AWS Web Console
- SSH keys for the AWS instances

## Steps

### Add Private Key to SSH Authentication Agent

Adding your key to the SSH Authentication Agent allows you to connect to servers *from* the host you're connecting to with the same credentials.

```bash
$ ssh-add ~/.ssh/ec2.pem
Identity added: /home/username/.ssh/ec2.pem (/home/username/.ssh/ec2.pem)
```

After the key is added, confirm with:

```bash
$ ssh-add -L
```

### SSH into Bastion

```bash
$ ssh -A -l ubuntu monitoring.treescount.foo.com
```

The `-A`  enables forwarding of the authentication agent connection so that the `.pem` file doesn't have to by copied to the bastion.

### SSH into an Application Server

This is the step where you need access to the AWS Web Console to determine the private IP address of an application server. Once obtained:

```bash
$ ssh 10.0.1.191
```

### Run Migrations

After successfully connecting to an application server, run `setupdb.sh`:

```bash
$ /opt/nyc-trees/scripts/setupdb.sh
```

This script will:

- Ensure that PostGIS is installed on the configured database
- Attempt to apply any outstanding migrations
- Attempt to create the training flatpages
