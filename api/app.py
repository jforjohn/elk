#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for, json

app = Flask(__name__)

sflow_fields = [
    {
        'id': 1,
        'sflow_field': u'sflow.srcIP', 
        'sflow_value': u'',
        'sendto_cluster': u'',
        'include': False,
        'monitoring': False
    },
    {
        'id': 2,
        'sflow_field': u'sflow.dstIP',
        'sflow_value': u'',
        'sendto_cluster': u'',
        'include': False,
        'monitoring': False
    },
    {
        'id': 3,
        'sflow_field': u'sflow.srcPort',
        'sflow_value': u'',
        'sendto_cluster': u'',
        'include': False,
        'monitoring': False
    },
    {
        'id': 4,
        'sflow_field': u'sflow.dstPort',
        'sflow_value': u'',
        'sendto_cluster': u'',
        'include': False,
        'monitoring': False
    },
    {
        'id': 5,
        'sflow_field': u'sflow.src_vlan',
        'sflow_value': u'',
        'sendto_cluster': u'',
        'include': False,
        'monitoring': False
    },
    {
        'id': 6,
        'sflow_field': u'sflow.dst_vlan',
        'sflow_value': u'',
        'sendto_cluster': u'',
        'include': False,
        'monitoring': False
    },
    {
        'id': 7,
        'sflow_field': u'sflow.IP_Protocol',
        'sflow_value': u'',
        'sendto_cluster': u'',
        'include': False,
        'monitoring': False
    }
    ]

sflow_fieldNames = list()
sflow_values = list()
sendto_clusters = list()

@app.route('/')
def index():
    return "Hello, World!" 

#@app.route('/logstash_config/api/v1.0/sflow_fields', methods=['GET'])
#def get_sflow_fields():
#    return jsonify({'sflow_fields': sflow_fields})

def make_public_sflow_field(sflow_field):
    new_sflow_field = {}
    for field in sflow_field:
        if field == 'id':
            new_sflow_field['uri'] = url_for('get_sflow_field', sflow_field_id=sflow_field['id'], _external=True)
        else:
            new_sflow_field[field] = sflow_field[field]
    return new_sflow_field

@app.route('/logstash_config/api/v1.0/sflow_fields', methods=['GET'])
def get_sflow_fields():
    return jsonify({'sflow_fields': [make_public_sflow_field(sflow_field) for sflow_field in sflow_fields]})

@app.route('/logstash_config/api/v1.0/sflow_fields/<int:sflow_field_id>', methods=['GET'])
def get_sflow_field(sflow_field_id):
    sflow_field = [sflow_field for sflow_field in sflow_fields if sflow_field['id'] == sflow_field_id]
    if len(sflow_field) == 0:
        abort(404)
    return jsonify({'sflow_field': sflow_field[0]})

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/logstash_config/api/v1.0/sflow_fields', methods=['POST'])
def create_sflow_field():
    if not request.json or not 'title' in request.json:
        abort(400)
    sflow_field = {
        'id': sflow_fields[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    sflow_fields.append(sflow_field)
    return jsonify({'sflow_field': sflow_field}), 201

@app.route('/logstash_config/api/v1.0/sflow_fields/<int:sflow_field_id>', methods=['PUT'])
def update_sflow_field(sflow_field_id):
    sflow_field = [sflow_field for sflow_field in sflow_fields if sflow_field['id'] == sflow_field_id]
    if len(sflow_field) == 0:
        abort(404)
    if not request.get_json(force=True):
        abort(400)
    #if 'sflow_field' in request.json and type(request.json['sflow_field']) != unicode:
    #    abort(400)
    if 'sflow_value' not in request.get_json(force=True) or type(request.get_json(force=True)['sflow_value']) != unicode:
        abort(400)
    if 'sendto_cluster' not in request.get_json(force=True) or type(request.get_json(force=True)['sendto_cluster']) != unicode:
        abort(400)
    if 'include' not in request.get_json(force=True) or type(request.get_json(force=True)['include']) != bool:
        abort(400)
    if 'monitoring' not in request.get_json(force=True) or type(request.get_json(force=True)['monitoring']) != bool:
        abort(400)
    #sflow_field[0]['sflow_field'] = request.json.get('sflow_field', sflow_field[0]['sflow_field'])
    #sflow_field[0]['include'] = request.json.get('include', sflow_field[0]['include'])
    sflow_field[0]['sflow_value'] = request.get_json(force=True)['sflow_value']
    sflow_field[0]['sendto_cluster'] = request.get_json(force=True)['sendto_cluster']
    sflow_field[0]['include'] = request.get_json(force=True)['include']
    sflow_field[0]['monitoring'] = request.get_json(force=True)['monitoring']
    logstash_config_changes(sflow_field[0])
    return jsonify({'sflow_field': sflow_field[0]})

#@app.route('/logstash_config/api/v1.0/sflow_fields/<int:sflow_field_id>', methods=['DELETE'])
#def delete_sflow_field(sflow_field_id):
#    sflow_field = [sflow_field for sflow_field in sflow_fields if sflow_field['id'] == sflow_field_id]
#    if len(sflow_field) == 0:
#        abort(404)
#    sflow_fields.remove(sflow_field[0])
#    return jsonify({'result': True})

def logstash_config_changes(add_sflow_field):
    if add_sflow_field['include'] == True:
        sflow_fieldNames.append(add_sflow_field['sflow_field'])
        sflow_values.append(add_sflow_field['sflow_value'])
        sendto_clusters.append(add_sflow_field['sendto_cluster'])
        if add_sflow_field['monitoring'] == True:
            DIR='/home/nectar/elk/compose_elk/logstash/config'
            filename='sflow_output.conf'
            try:
                conf_file = open(DIR+'/'+filename,'w')
            except:
                print 'File cannot be opened:', filename
            conf_file.write('output {\n     if [type] == "sflow" {\n        stdout { codec => rubydebug }\n')
            changes = sorted(zip(sendto_clusters,sflow_fieldNames,sflow_values))
            init = changes[0][0]
            newIF = True
            #TODO make a name for elasticsearch host
            #TODO run forward sflow from logstash-forwarfer to logstash
            #TODO run docker-compose for elk with the appropriate link names

            for cluster,field,value in changes:
                if cluster != init:
                    conf_file.write('{\n            elasticsearch { protocol => "http"  cluster => "%s" host => elasticsearch}\n    }\n' %(init))
                    newIF = True
                    init = cluster
                if newIF == True:
                    conf_file.write('        if [%s] == "%s" ' %(field,value))
                else:
                    conf_file.write('and [%s] == "%s"' %(field,value))
                newIF = False
            conf_file.write('{\n            elasticsearch { protocol => "http"  cluster => "%s" host => elasticsearch}\n    }\n     }\n}' %(init))
            conf_file.close()
    return 0

if __name__ == '__main__':
    app.run(
            host=app.config.get("HOST", "192.168.56.101"),
            debug=True
           )
