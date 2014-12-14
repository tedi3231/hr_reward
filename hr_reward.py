# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr__reward_policy_category(osv.Model):

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "hr.reward.policy.category"
    _description = "Policy Category"
    _columns = {
        'name': fields.char("Policy Category", required=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'parent_id': fields.many2one('hr.reward.policy.category', 'Parent Policy Category', select=True),
        'child_ids': fields.one2many('hr.reward.policy.category', 'parent_id', 'Child Categories'),
        'order_num':fields.integer(string='Order num',required=True),
        'color':fields.char(string='Color', size=7),
        #'employee_ids': fields.many2many('hr.employee', 'employee_category_rel', 'category_id', 'emp_id', 'Employees'),
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from hr_reward_policy_category where id IN %s', (tuple(ids), ))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive Categories.', ['parent_id'])
    ]

class hr_reward_policy(osv.Model):
    _name = 'hr.reward.policy'

    _columns = {
        'name' : fields.char("Policy name",size=500,required=True),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'category_id':fields.many2one('hr.reward.policy.category','Policy Ctegory',required=True),
        'policy_items':fields.one2many('hr.reward.policy.item','policy_id',string='Policy items')
    }

class hr_reward_policy_item(osv.Model):
    _name = 'hr.reward.policy.item'

    _columns = { 
        'policy_id':fields.many2one('hr.reward.policy','Policy'),
        'content_type':fields.selection([('text','Text'),('image','Image'),('video','Video')],string='Content type'),
        #'content':fields.function(),
        'content_text':fields.text(string='Content'),
        'content_binary':fields.binary(string='Binary content',filters='*.png,*.gif,*.mp4,*.jpg,*.jpeg'),
        'add_date':fields.date(string='Add date'),
    }