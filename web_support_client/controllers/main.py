# -*- coding: utf-8 -*-
import functools
from cStringIO import StringIO
import openerp
import openerp.modules.registry
from openerp.modules import get_module_resource
from openerp import http
from openerp.http import request
db_list = http.db_list

db_monodb = http.db_monodb


class UserImage(http.Controller):

    @http.route('/web/user/image', type='http', auth="none", cors="*")
    def user_image(self, user_id, dbname=None, **kw):
        imgname = 'user_image.png'
        placeholder = functools.partial(
            get_module_resource, 'web', 'static', 'src', 'img')

        if request.session.db:
            dbname = request.session.db
        elif dbname is None:
            dbname = db_monodb()
        if not dbname:
            response = http.send_file(placeholder(imgname))
        else:
            try:
                # create an empty registry
                registry = openerp.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    cr.execute("""SELECT p.image_small, p.write_date
                                    FROM res_partner p
                               LEFT JOIN res_users u
                                      ON u.partner_id = p.id
                                   WHERE u.id = %s
                               """, (user_id,))
                    row = cr.fetchone()
                    if row and row[0]:
                        image_data = StringIO(str(row[0]).decode('base64'))
                        response = http.send_file(
                            image_data, filename=imgname, mtime=row[1])
                    else:
                        response = http.send_file(
                            placeholder('placeholder.png'))
            except Exception:
                response = http.send_file(placeholder(imgname))

        return response
