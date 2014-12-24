openerp.hr_reward = function (instance) {

    alert('heelo');

    instance.hr_reward.btn_review = function(parent, action){
        var self = this;
        alert('test');
        // and do something...
        return false;
    };

    instance.web.client_actions.add('reward.btn_review', 'instance.hr_reward.btn_review');

};