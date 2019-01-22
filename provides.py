from charms.reactive import when_any
from charms.reactive import set_flag, clear_flag
from charms.reactive import Endpoint


class MountProvides(Endpoint):

    @when_any('endpoint.{endpoint_name}.changed',
              'endpoint.{endpoint_name}.departed')
    def changed(self):
        set_flag(self.expand_name('{endpoint_name}.changed'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.changed'))
        clear_flag(self.expand_name('endpoint.{endpoint_name}.departed'))

    def get_mount_requests(self):
        return [{
            'identifier': relation.relation_id,
            'application_name': relation.joined_units.received_raw.get(
                'export_name', relation.application_name),
            'addresses': [
                unit.received_raw.get('ingress-address',
                                      unit.received_raw['private-address'])
                for unit in relation.joined_units],
        } for relation in self.relations]

    def configure(self, responses):
        for response in responses:
            relation = self.relations[response['identifier']]
            relation.to_publish_raw.update({
                'mountpoint': response['mountpoint'],
                'fstype': response['fstype'],
                'options': response['options'],
            })
            for key in ('export_name', 'hostname'):
                if key in response:
                    relation.to_publish_raw[key] = response[key]
                elif key in relation.to_publish_raw:
                    del relation.to_publish_raw[key]
        clear_flag(self.expand_name('{endpoint_name}.changed'))
