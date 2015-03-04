# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ApplicationEC2Images.owner'
        db.delete_column(u'citizengrid_applicationec2images', 'owner_id')

        # Deleting field 'ApplicationOpenstackImages.owner'
        db.delete_column(u'citizengrid_applicationopenstackimages', 'owner_id')


    def backwards(self, orm):
        # Adding field 'ApplicationEC2Images.owner'
        db.add_column(u'citizengrid_applicationec2images', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=orm['auth.User'], to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'ApplicationOpenstackImages.owner'
        db.add_column(u'citizengrid_applicationopenstackimages', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=orm['auth.User'], to=orm['auth.User']),
                      keep_default=False)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'citizengrid.applicationbasicinfo': {
            'Meta': {'object_name': 'ApplicationBasicInfo'},
            'branch': ('django.db.models.fields.related.ManyToManyField', [], {'default': "'NONE'", 'to': u"orm['citizengrid.Branch']", 'symmetrical': 'False'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'default': "'NONE'", 'to': u"orm['citizengrid.Category']", 'symmetrical': 'False'}),
            'client_downloads': ('django.db.models.fields.IntegerField', [], {}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'iconfile': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '128'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'public': ('django.db.models.fields.BooleanField', [], {}),
            'subcategory': ('django.db.models.fields.related.ManyToManyField', [], {'default': "'NONE'", 'to': u"orm['citizengrid.SubCategory']", 'symmetrical': 'False'})
        },
        u'citizengrid.applicationclientinfo': {
            'Meta': {'object_name': 'ApplicationClientInfo'},
            'appref': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.ApplicationBasicInfo']"}),
            'client_image_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'client_image_location': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'clienthost': ('django.db.models.fields.CharField', [], {'default': "'Local'", 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'citizengrid.applicationec2images': {
            'Meta': {'object_name': 'ApplicationEC2Images'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.ApplicationBasicInfo']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'image_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'zone_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'zone_url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'citizengrid.applicationfile': {
            'Meta': {'object_name': 'ApplicationFile'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.ApplicationBasicInfo']", 'null': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'file_format': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '4'}),
            'file_type': ('django.db.models.fields.CharField', [], {'default': "'T'", 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'citizengrid.applicationopenstackimages': {
            'Meta': {'object_name': 'ApplicationOpenstackImages'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.ApplicationBasicInfo']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'image_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'zone_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'zone_url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'citizengrid.applicationserverinfo': {
            'Meta': {'object_name': 'ApplicationServerInfo'},
            'apphost': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '64'}),
            'appref': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.ApplicationBasicInfo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server_image_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'server_image_location': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'citizengrid.branch': {
            'Meta': {'object_name': 'Branch'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'citizengrid.category': {
            'Meta': {'object_name': 'Category'},
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.Branch']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'citizengrid.cgview': {
            'Meta': {'object_name': 'CGView', 'managed': 'False'},
            'category_id': ('django.db.models.fields.IntegerField', [], {}),
            'category_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'subcategory_id': ('django.db.models.fields.IntegerField', [], {}),
            'subcategory_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'citizengrid.cloudinstancesopenstack': {
            'Meta': {'object_name': 'CloudInstancesOpenstack'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.ApplicationBasicInfo']"}),
            'application_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.ApplicationOpenstackImages']"}),
            'credentials': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.UserCloudCredentials']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_id': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'citizengrid.subcategory': {
            'Meta': {'object_name': 'SubCategory'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizengrid.Category']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'citizengrid.usercloudcredentials': {
            'Meta': {'object_name': 'UserCloudCredentials'},
            'access_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'host_cloud': ('django.db.models.fields.CharField', [], {'default': "'Other'", 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_alias': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'citizengrid.userinfo': {
            'Meta': {'object_name': 'UserInfo'},
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'primary_key': 'True'}),
            'user_primary_role': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'user_primary_role_desc': ('django.db.models.fields.CharField', [], {'default': "'Not Set'", 'max_length': '128'}),
            'user_status': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['citizengrid']