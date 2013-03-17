/**
 * Created with PyCharm.
 * User: Zhou Guangwen
 * Date: 3/17/13
 * Time: 6:40 PM
 * To change this template use File | Settings | File Templates.
 */

openerp.upcas = function (instance) {
    instance.web.Login = instance.web.Login.extend({
        start: function () {
            console.log("I am here!");
            return this._super.apply(this, arguments);
        }
    })
}