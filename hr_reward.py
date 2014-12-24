# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_reward_group(osv.Model):
    _name = 'hr.reward.group'
    
    _columns = {
        'name':fields.char(string='Policy group',required=True),
    }

class hr_employee(osv.Model):
    _inherit='hr.employee'

    def _get_policies(self,cr,uid,ids,name, args, context=None):
        values = {}
        sql = """select distinct hrp.id from hr_reward_policy as hrp join policy_group_rel as prl
                on hrp.id = prl.policy_id 
                join hr_reward_group as hrg
                on hrg.id = prl.group_id 
                where hrg.id in (%s)"""

        print 'employee ids is %s ' % ids
        
        for item in self.read(cr,uid,ids,['id','reward_groups'],context=context):
            if item['reward_groups']:
                cr.execute(sql % ','.join([str(sitem) for sitem in item['reward_groups']]))
                policy_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                print 'policy_ids is %s' % policy_ids
                values[item['id']] = policy_ids
                print 'values is %s ' % values
        
        """
        for item_id in ids:
            values[item_id] = [1,2,3]
        """
        return values


    def _get_group(self,cr, uid, context=None):
        dataobj = self.pool.get('ir.model.data')
        result = []
        try:
            dummy,group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'hr_reward', 'reward_employee')
            result.append(group_id)
        except ValueError:
            # If these groups does not exists anymore
            pass
        return result


    def create(self,cr,uid,data,context=None):
        print 'create employee ,data is %s' % data
        emp_id = super(hr_employee,self).create(cr,uid,data,context=context)
        print 'emp_id is %s' % emp_id
        rel_user = {
            'name':data['employee_no'],
            'login':data['employee_no'],
            'password':data['employee_no'],
            'groups_id':[[6,False,self._get_group(cr,uid,context=context)]] ,
            'active':True,
            'company_id':self.pool.get('res.users').browse(cr, uid, uid,context=context).company_id.id,
        }
        print 'rel_user is %s' % rel_user
        user_id = self.pool.get('res.users').create(cr,uid,rel_user,context=context)
        if user_id:
            self.write(cr,uid,[emp_id],{'user_id':user_id},context=context)
        print 'user_id is %s' % user_id
        #TODO 为当前用户设置默认的权限组
        return emp_id

    _columns = {
        'employee_no':fields.char(string='Employee No',required=True,size=100),
        'reward_groups':fields.many2many('hr.reward.group','employee_group_rel','emp_id','group_id',string='Reward groups'),
        'policies':fields.function(_get_policies,type='one2many',relation='hr.reward.policy',string='Policies'),
    }

    _sql_constraints = [('employee_no_uniq','unique(employee_no)', 'Employee no must be unique!')]

class hr_reward_policy_category(osv.Model):

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

    def act_review(self, cr, uid, ids, context=None):
        print 'act_review called!'
        context={}
        context["key"]="value"
                
        ret = {
            'type': 'ir.actions.client',
            'tag': 'reward.btn_review',
            'context':context,
        }
        return ret
    
    _columns = {
        'name' : fields.char("Policy name",size=500,required=True),
        #'employee_id':fields.many2one('hr.employee','Employee'),
        'category_id':fields.many2one('hr.reward.policy.category','Policy Ctegory',required=True),
        'policy_items':fields.one2many('hr.reward.policy.item','policy_id',string='Policy items'),
        'reward_groups':fields.many2many('hr.reward.group','policy_group_rel','policy_id','group_id','Reward groups'),
    }

class hr_reward_policy_item(osv.Model):
    _name = 'hr.reward.policy.item'

    _columns = { 
        'policy_id':fields.many2one('hr.reward.policy','Policy'),
        'content_type':fields.selection([('text','Text'),('image','Image'),('video','Video')],string='Content type'),
        #'content':fields.function(),
        'content_text':fields.text(string='Content'),
        'content_binary':fields.binary(string='Binary content',filters='*.png,*.gif,*.mp4,*.jpg,*.jpeg'),
        'order_num':fields.integer(string='Order num'),
    }
