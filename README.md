# Overview

This charm implements Manila charm subordinate that enables and configures
the [Pure Storage FlashBlade share backend][flashblade-shared-fs-upstream] for use with
Charmed Openstack.

> **Note**: The manila-flashblade charm is currently in tech-preview.

# Configuration

To display all configuration option information run `juju config <application>`.
If the application is not deployed then see the charm's
[Configure tab][charm-manila-flashblade-configure] in the Charmhub.
Finally, the [Juju documentation][juju-docs-config-apps] provides general
guidance on configuring applications.

# Deployment

The charm can be deployed through a bundle or manually like described below:

    juju deploy manila --channel <channel>
    juju deploy manila-flashblade --channel <channel>
    juju add-relation manila-flashblade:manila-plugin manila:manila-plugin

# High availability

The charm can be used to enable a Pure Storage FlashBlade backend in highly available
Charmed Manila deployments. Please see example overlay bundle for such
deployments in the [Manila Charm Deployment Guide][cdg-manila].

# Deferred service events

This charm supports the deferred service events feature.

Operational or maintenance procedures applied to a cloud often lead to
the restarting of various OpenStack services and/or the calling of certain
charm hooks. Although normal, such events can be undesirable due to the service
interruptions they can cause.

The deferred service events feature provides the operator the choice of
preventing these service restarts and hook calls from occurring, which can then
be resolved at a more opportune time.

See [Deferred service events][cg-deferred-service-events] for more
information on this feature.

# Documentation

The OpenStack Charms project maintains two documentation guides:

* [OpenStack Charm Guide][cg]: the primary source of information for
  OpenStack charms
* [OpenStack Charms Deployment Guide][cdg]: a step-by-step guide for
  deploying OpenStack with charms

# Bugs

Please report bugs on [Launchpad][lp-bugs-charm-manila-flashblade].

<!-- LINKS -->

[cg]: https://docs.openstack.org/charm-guide
[cdg]: https://docs.openstack.org/project-deploy-guide/charm-deployment-guide
[cg-deferred-service-events]: https://docs.openstack.org/charm-guide/latest/admin/deferred-events.html
[flashblade-shared-fs-upstream]: https://docs.openstack.org/manila/latest/configuration/shared-file-systems/drivers/purestorage-flashblade-driver.html
[manila-upstream]: https://docs.openstack.org/manila
[manila-charm]: https://charmhub.io/manila
[charm-manila-purestorage-configure]: https://charmhub.io/charm-manila-flashblade/configure
[juju-docs-config-apps]: https://juju.is/docs/olm/configure-an-application
[lp-bugs-charm-manila-purestorage]: https://bugs.launchpad.net/charm-manila-flashblade/+filebug
[cdg-manila]: https://docs.openstack.org/project-deploy-guide/charm-deployment-guide/latest/manila-ganesha.html
