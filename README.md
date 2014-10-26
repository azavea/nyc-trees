nyc-trees
=========

NYC Parks Trees Count! 2015 tree census

## Local Development

A combination of Vagrant 1.5+ and Ansible 1.6+ is used to setup the development environment for this project. It of the following virtual machines:

- `app`
- `tiler`
- `services`

The `app` virtual machine contains an instance of the Django application, `tiler` contains a tiling server, and `services` contains shared resources of `app` and `tiler`:

- PostgreSQL
- Redis
- Logstash
- Kibana

Use the following command to bring up a local development environment:

```bash
$ vagrant up
```

After provisioning is complete, you can bring up the Django `runserver` from within the `app` virtual machine with the following commands:

```bash
$ vagrant ssh app
vagrant@app:~$ envdir /etc/nyc-trees.d/env /opt/app/manage.py runserver
```

**Note**: If you get an error that resembles the following, try logging into the `app` virtual machine again for the group permissions changes to take effect:

```
envdir: fatal: unable to switch to directory /etc/nyc-trees.d/env: access denied
```

### Caching

In order to speed up things up, you may want to consider using a local caching proxy. The `VAGRANT_PROXYCONF_ENDPOINT` environmental variable provides a way to supply a caching proxy endpoint for the virtual machines to use:

```bash
$ VAGRANT_PROXYCONF_ENDPOINT="http://192.168.96.10:8123/" vagrant up
```

### Log Aggregation

In order to view the Kibana web UI, navigate to the following URL from a browser on the virtual machine host:

```
http://localhost:8081/index.html#/dashboard/file/logstash.json
```
