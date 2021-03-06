import os
import bottle
import _dynStruct

def check_block_id(block_id):
    if not block_id or block_id == "None":
        return None
    try:
        block_id = int(block_id)
    except:
        return False
    if block_id < 0 or block_id >= len(_dynStruct.l_block):
        return False
    return block_id

def check_struct_id(id_struct):
    if not id_struct or id_struct == "None":
        return None
    if not _dynStruct.Struct.get_by_id(id_struct):
        return False
    return id_struct

def check_id_member_from_access(id_member):
    if not id_member or id_member == "None":
        return None
    if not _dynStruct.Struct.get_by_id(id_member):
        return False
    return id_member

@bottle.route("/block")
def block_view():
    block_id = check_block_id(bottle.request.query.id)

    if block_id or block_id == 0:
        return bottle.template("block_view", block=_dynStruct.l_block[block_id])
    else:
        return bottle.template("error", msg="Bad block id")

@bottle.route("/block_search")
def block_search():
    id_struct = check_struct_id(bottle.request.query.id_struct)

    if id_struct == False:
            return bottle.template("error", msg="Bad struct id")
    else:
        return bottle.template("block_search", id_struct=id_struct)

@bottle.route("/block_get")
def block_get():
    id_struct = check_struct_id(bottle.request.query.id_struct)

    return _dynStruct.block_json(id_struct, bottle.request.query)
    
@bottle.route("/access_search")
def access_search():
    id_block = check_block_id(bottle.request.query.id_block)
    id_member = check_id_member_from_access(bottle.request.query.id_member)

    if id_block != 0 and id_block == False:
            return bottle.template("error", msg="Bad block id")
    elif id_member != 0 and id_member == False:
            return bottle.template("error", msg="Bad struct id")
    else:
        return bottle.template("access_search", id_block=id_block, id_member=id_member)

@bottle.route("/access_get")
def access_get():
    id_block = check_block_id(bottle.request.query.id_block)
    id_member = check_id_member_from_access(bottle.request.query.id_member)

    return _dynStruct.access_json(id_block, id_member, bottle.request.query)

@bottle.route("/struct")
def struct_view():
    struct = _dynStruct.Struct.get_by_id(bottle.request.query.id)

    if not struct:
        return bottle.template("error", msg="Bad struct id")    

    return bottle.template("struct_view", struct=struct, edit=False)

@bottle.route("/struct_edit")
def struct_edit():
    struct = _dynStruct.Struct.get_by_id(bottle.request.query.id)

    if not struct:
        return bottle.template("error", msg="Bad struct id")
    
    return bottle.template("struct_view", struct=struct, edit=True)

@bottle.route("/struct_do_edit", method='POST')
def struct_do_edit():
    struct = _dynStruct.Struct.get_by_id(bottle.request.query.id)

    if not struct:
        return bottle.template("error", msg="Bad struct id")

    struct.name = bottle.request.forms.name
    _dynStruct.save_modif()
    
    bottle.redirect("/struct?id=%d" % (struct.id))

@bottle.route("/struct_remove")
def struct_remove():
    struct = _dynStruct.Struct.get_by_id(bottle.request.query.id)

    if not struct:
        return bottle.template("error", msg="Bad struct id")

    struct.remove_all_block()
    _dynStruct.l_struct.remove(struct)
    _dynStruct.save_modif()
    
    bottle.redirect("/struct_search")

@bottle.route("/struct_create")
def struct_create():
    return bottle.template("struct_create")

@bottle.route("/struct_do_create", method='POST')
def struct_do_create():
    size = bottle.request.forms.size
    try:
        size = int(size)
    except ValueError:
        return bottle.template("error", msg="Size is not in integer")

    if size <= 0:
        return bottle.template("error", msg="Size have to be positive")

    new_struct = _dynStruct.Struct(None)
    new_struct.id = _dynStruct.l_struct[-1].id + 1
    new_struct.name = bottle.request.forms.name
    new_struct.size = size
    new_struct.add_pad()

    _dynStruct.l_struct.append(new_struct)
    _dynStruct.save_modif()
    
    bottle.redirect("/struct?id=%d" % (new_struct.id))
    
@bottle.route("/struct_search")
def struct_search():
    return bottle.template("struct_search")

@bottle.route("/struct_get")
def struct_get():
    return _dynStruct.struct_json()

@bottle.route("/struct_edit_instance")
def struct_edit_instance():
    struct = _dynStruct.Struct.get_by_id(bottle.request.query.id_struct)

    if not struct:
        return bottle.template("error", msg="Bad struct id")

    return bottle.template("edit_block_list", id_struct=struct.id, struct_name=struct.name)


@bottle.route("/member_get")
def member_get():
    id_struct = bottle.request.query.id_struct
    return _dynStruct.member_json(_dynStruct.Struct.get_by_id(id_struct), id_struct)

def member_template(query, edit):
    id_struct = check_struct_id(query.id_struct)
    id_member = query.id_member

    if id_member != 0 and not id_member:
        return bottle.template("error", msg="member id missing")

    if id_struct != 0 and not id_struct:
        return bottle.template("error", msg="Bad struct id")

    member = _dynStruct.Struct.get_member_by_id(id_struct, int(id_member))

    if not member:
        return bottle.template("error", msg="bad member id")    

    return bottle.template("member_view",
                           id_member="%s.%d" % (id_struct, member.offset),
                           member=member,
                           name_member=_dynStruct.Struct.make_member_name(id_struct, member.offset),
                           edit=edit)
    
@bottle.route("/member")
def member_view():
    return(member_template(bottle.request.query, False))

@bottle.route("/member_edit")
def member_edit():
    return(member_template(bottle.request.query, True))

@bottle.route("/member_do_edit", method='POST')
def member_do_edit():
    id_struct = check_struct_id(bottle.request.query.id_struct)
    id_member = bottle.request.query.id_member

    if id_member != 0 and not id_member:
        return bottle.template("error", msg="member id missing")

    if not id_struct:
        return bottle.template("error", msg="Bad struct id")

    struct = _dynStruct.Struct.get_by_id(id_struct)    
    if not struct:
        return bottle.template("error", msg="bad struct id")

    member = struct.get_member(int(id_member))
    next_member = struct.get_member(int(id_member) + member.size)

    try:
        member.edit(bottle.request.forms, next_member, struct.size)
    except ValueError as err:
        return bottle.template("error", msg=str(err))

    # if next member is padding remove it, add_pad will set a new padding with
    # correct size + offset if needed
    if next_member and next_member.is_padding:
        struct.members.remove(next_member)

    struct.add_pad()
    _dynStruct.save_modif()
    bottle.redirect("/member?id_struct=%s&id_member=%s" % (id_struct, id_member))

@bottle.route("/member_remove")
def member_remove():
    id_struct = check_struct_id(bottle.request.query.id_struct)
    id_member = bottle.request.query.id_member

    if id_member != 0 and not id_member:
        return bottle.template("error", msg="member id missing")

    if id_struct != 0 and not id_struct:
        return bottle.template("error", msg="Bad struct id")
    id_struct = str(id_struct)

    struct = _dynStruct.Struct.get_by_id(id_struct)    
    if not struct:
        return bottle.template("error", msg="bad struct id")

    member = struct.get_member(int(id_member))
    next_member = struct.get_member(int(id_member) + member.size)

    prev_member = None
    if struct.members.index(member) > 0:
        prev_member = struct.members[struct.members.index(member) - 1]

    struct.members.remove(member)

    # by removing the next or previous padding a new padding with the size
    # of the old padding + the size of removed member will be created
    if next_member and next_member.is_padding:
        struct.members.remove(next_member)
    if prev_member and prev_member.is_padding:
        struct.members.remove(prev_member)
    
    struct.add_pad()
    
    _dynStruct.save_modif()
    bottle.redirect("/struct?id=%s" % (id_struct))

@bottle.route("/member_create")
def member_create():
    id_struct = check_struct_id(bottle.request.query.id_struct)
    id_member = bottle.request.query.id_member

    if not id_member:
        return bottle.template("error", msg="member id missing")

    if not id_struct:
        return bottle.template("error", msg="Bad struct id")

    member = _dynStruct.Struct.get_by_id("%s.%s" % (id_struct, id_member))

    if not member:
        return bottle.template("error", msg="Bad member id")        

    if not member.is_padding:
        return bottle.template("error", msg="To add a member, member_id have to point to a padding member")
    
    return bottle.template("member_create", id_struct=id_struct, member=member)

@bottle.route("/member_do_create", method='POST')
def member_do_create():
    id_struct = check_struct_id(bottle.request.query.id_struct)
    id_member = bottle.request.query.id_member

    if not id_member:
        return bottle.template("error", msg="member id missing")

    if not id_struct:
        return bottle.template("error", msg="Bad struct id")

    struct = _dynStruct.Struct.get_by_id(id_struct)    
    if not struct:
        return bottle.template("error", msg="bad struct id")

    member = struct.get_member(int(id_member))

    if not member:
        return bottle.template("error", msg="Bad member id")        

    if not member.is_padding:
        return bottle.template("error", msg="To add a member, member_id have to point to a padding member")

    try:
        struct.add_member_from_web_ui(member, bottle.request.forms)
    except ValueError as err:
        struct.add_pad()
        return bottle.template("error", msg=str(err))
        
    struct.members.remove(member)
    struct.add_pad()
    _dynStruct.save_modif()
    if '.' in id_struct:
        bottle.redirect("/member?id_struct=%s&id_member=%s" % (id_struct[:id_struct.rfind('.')], id_struct[id_struct.rfind('.') + 1:]))
    else:
        bottle.redirect("/struct?id=%s" % (id_struct))

@bottle.route("/header.h")
def dl_header():
    bottle.response.content_type = 'text/x-c'
    return _dynStruct.get_header(_dynStruct.l_struct)

@bottle.route("/static/<filename:path>")
def serve_static(filename):
    return bottle.static_file(filename, root=os.path.join(os.path.dirname(__file__), "static"))

@bottle.route("/remove_struct")
def remove_struct_from_block():
    id_block = check_block_id(bottle.request.query.id_block)

    if id_block != 0 and not id_block:
        return bottle.template("error", msg="Bad block id")

    _dynStruct.l_block[id_block].struct.remove_block(_dynStruct.l_block[id_block])
    _dynStruct.save_modif()
    bottle.redirect("/block?id=%d" % (id_block))

@bottle.route("/add_to_struct")
def add_to_struct_struct_from_block():
    id_block = check_block_id(bottle.request.query.id_block)

    if id_block != 0 and not id_block:
        return bottle.template("error", msg="Bad block id")
    return bottle.template("struct_select", id_block=id_block)

@bottle.route("/do_add_to_struct")
def add_to_struct_struct_from_block():
    id_block = check_block_id(bottle.request.query.id_block)
    id_struct = check_struct_id(bottle.request.query.id_struct)

    if id_block != 0 and not id_block:
        return bottle.template("error", msg="Bad block id")

    if not id_struct:
        return bottle.template("error", msg="Bad struct id")

    block = _dynStruct.l_block[id_block]
    if block.struct:
        return bottle.template("error", msg="Block already linked")
    struct = _dynStruct.Struct.get_by_id(id_struct)
    struct.add_block(block)
    _dynStruct.save_modif()
    return bottle.template("block_view", block=block)

@bottle.route("/struct_select_get")
def get_list_compat_struct():
    id_block = check_block_id(bottle.request.query.id_block)
    return _dynStruct.struct_select_json(id_block)    

@bottle.route("/struct_instance_get")
def struct_instance_get():
    id_struct = check_struct_id(bottle.request.query.id_struct)

    if not id_struct:
        return bottle.template("error", msg="Bad struct id")

    struct = _dynStruct.Struct.get_by_id(id_struct)    
    if not struct:
        return bottle.template("error", msg="bad struct id")

    instance = True if bottle.request.query.instance == "true" else False

    return(_dynStruct.struct_instances_json(struct, instance))

@bottle.route("/struct_instance_do_edit", method='POST')
def struct_instance_do_edit():
    id_struct = check_struct_id(bottle.request.query.id)

    if not id_struct:
        return bottle.template("error", msg="Bad struct id")

    struct = _dynStruct.Struct.get_by_id(id_struct)
    if not struct:
        return bottle.template("error", msg="bad struct id")

    if bottle.request.forms.add != '':
        for add in bottle.request.forms.add.split(','):
            struct.add_block(_dynStruct.l_block[int(add)])

    if bottle.request.forms.remove != '':
        for remove in bottle.request.forms.remove.split(','):
            struct.remove_block(_dynStruct.l_block[int(remove)])

    _dynStruct.save_modif()

@bottle.route("/struct_do_detect")
def struct_do_detect():
    id_struct = check_struct_id(bottle.request.query.id_struct)
    if not id_struct:
        return bottle.template("error", msg="Bad struct id")
    struct = _dynStruct.Struct.get_by_id(id_struct)
    struct.detect(_dynStruct.l_block) 
    _dynStruct.save_modif()
    bottle.redirect("/struct?id=%s" % (id_struct))

@bottle.route("/do_recovery")
def do_recovery():
    block_id = check_block_id(bottle.request.query.id_block)
    if not block_id and block_id != 0:
        return bottle.template("error", msg="Bad block id")
    block = _dynStruct.l_block[block_id]
    if not block.struct:
        new_struct = _dynStruct.Struct(block)
        new_struct.clean_struct()
        try:
            new_struct.id = _dynStruct.l_struct[-1].id + 1;
        except IndexError:
            new_struct.id = 1
        new_struct.set_default_name()
        _dynStruct.l_struct.append(new_struct)
        _dynStruct.save_modif()
    else:
        return bottle.template("error", msg="Block already linked")
    bottle.redirect("/block?id=%d" % (block_id))

@bottle.route("/quit")
def quit():
    return bottle.template("quit")

@bottle.route("/do_quit")
def do_quit():
    os._exit(0)

@bottle.route("/")
def index():
    bottle.redirect("/block_search")


def start_webui(addr, port):
    bottle.TEMPLATE_PATH.insert(0, os.path.dirname(__file__) + "/views")
    print("Starting web server at http://%s:%s" % (addr, port))
    bottle.run(host=addr, port=port, quiet=True)
