import configparser
import logging
import os

from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized

import logic

from flask import Flask, render_template, request, flash, redirect, url_for

import spell

# Application Setup
here = os.path.dirname(__file__)
site_config = configparser.RawConfigParser()
ini_path = os.path.join(here, 'configuration.ini')
site_config.read_file(open(ini_path))

SITE_TYPE = site_config.get('DEFAULT', 'site_type')
SITE_VERSION = site_config.get('DEFAULT', 'site_version')

app = Flask(__name__)
fh = logging.FileHandler(site_config.get('path', 'flask_log'))
app.logger.addHandler(fh)
app.secret_key = ('this_is_a_secret')
app.config['SITE_TYPE'] = SITE_TYPE
app.config['SITE_VERSION'] = SITE_VERSION
app.config['DISCORD_CLIENT_ID'] = site_config.get('discord', 'client_id')
app.config['DISCORD_CLIENT_SECRET'] = site_config.get('discord', 'client_secret')
if SITE_TYPE == 'Development':
    app.config['DISCORD_REDIRECT_URI'] = "http://localhost:5001/callback"
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "true"
else:
    app.config['DISCORD_REDIRECT_URI'] = "https://eqdb.net/callback"
app.config['DISCORD_BOT_TOKEN'] = ""


discord = DiscordOAuth2Session(app)

app_path = site_config.get('path', 'app_log')
formatter = logging.Formatter(
    '%(asctime)s: %(levelname)s - %(funcName)s - %(message)s',
    '%m/%d/%Y-%I%M%S %p')

app_log = logging.getLogger('app_log')
afh = logging.FileHandler(app_path)
afh.setFormatter(formatter)
app_log.addHandler(afh)
app_log.setLevel(logging.DEBUG)
ALLOWED_EXTENSIONS = {'txt'}

""" MAIN METHODS """


@app.route("/login/")
def login():
    return discord.create_session(scope=['identify'])


@app.route("/callback/")
def callback():
    discord.callback()
    return redirect(url_for("identify_attributed"))


@app.route("/identify/")
def identify():
    if SITE_TYPE == 'Beta':
        flash('Item Identification is not supported on Beta site')
        return redirect(url_for('error'))
    return render_template('identify_landing.html')


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))


@app.route("/identify/attributed/", methods=['GET', 'POST'])
@requires_authorization
def identify_attributed():
    if SITE_TYPE == 'Beta':
        flash('Item Identification is not supported on Beta site')
        return redirect(url_for('error'))
    user = discord.fetch_user()
    if request.method == 'GET':
        item = logic.get_unidentified_item(user=user)
        return render_template('identify.html', item=item)
    else:
        data = request.form
        # Do some validation
        if data['expansion'] == 'None' and data['source'] == 'None':
            flash('You must at least specify the expansion and source for an item identification.')
            return redirect(url_for('identify_attributed'))
        data = logic.add_item_identification(data, user=user)
        item = logic.get_item_data(data.get('item_id'))
        return render_template('identify_result.html', item=item, data=data)


@app.route("/identify/unattributed/", methods=['GET', 'POST'])
def identify_unattributed():
    if SITE_TYPE == 'Beta':
        flash('Item Identification is not supported on Beta site')
        return redirect(url_for('error'))
    if request.method == 'GET':
        item = logic.get_unidentified_item()
        return render_template('identify.html', item=item)
    else:
        data = request.form
        data = logic.add_item_identification(data)
        item = logic.get_item_data(data.get('item_id'))
        return render_template('identify_result.html', item=item, data=data)


@app.route("/search/tradeskill", methods=['GET', 'POST'])
def tradeskill_search():
    if request.method == 'GET':
        return render_template('tradeskill_search.html')
    else:
        tradeskill_name = request.form['tradeskill_name']
        trivial = request.form.get('trivial')
        tradeskill = request.form.get('tradeskill')
        if tradeskill == 'None':
            tradeskill = None
        if len(tradeskill_name) > 50:
            flash('Search by name limited to 50 characters.')
            return redirect(url_for('tradeskill_search'))
        elif 0 < len(tradeskill_name) < 3:
            flash('Search by name requires at least 3 characters.')
            return redirect(url_for('tradeskill_search'))
        if not tradeskill_name.isascii():
            flash('Only ASCII characters are allowed.')
            return redirect(url_for('tradeskill_search'))
        data = logic.get_tradeskills(name=tradeskill_name, trivial=trivial, tradeskill=tradeskill)
        return render_template('tradeskill_search_result.html', data=data)


@app.route("/tradeskill/detail/<int:ts_id>")
def tradeskill_detail(ts_id):
    data = logic.get_tradeskill_detail(ts_id)
    return render_template('tradeskill_detail.html', data=data)


@app.route("/npc/raw/<int:npc_id>")
def npc_raw(npc_id):
    raw_data = logic.get_npc_raw_data(npc_id)
    return render_template('raw_data.html', data=raw_data)


@app.route("/npc/detail/<int:npc_id>")
def npc_detail(npc_id):
    return render_template('npc_detail.html', data=logic.get_npc_detail(npc_id))


@app.route("/zone/detail/<int:zone_id>")
def zone_detail(zone_id):
    return render_template('zone_detail.html', data=logic.get_zone_detail(zone_id))


@app.route("/zone/listing")
def zone_listing():
    return render_template('zone_listing.html', data=logic.get_zone_listing())


@app.route("/identify/leaderboard/", methods=['GET'])
def identify_leaderboard():
    if SITE_TYPE == 'Beta':
        flash('Item Identification is not supported on Beta site')
        return redirect(url_for('error'))
    data = logic.get_leaderboard()
    return render_template('identify_leaderboard.html', data=data)


@app.route("/tooltip/<item_id>", methods=['GET', 'POST'])
def tooltip(item_id):
    return render_template('tooltip.html', item=logic.get_item_data(item_id))


@app.route("/spell-tooltip/<spell_id>", methods=['GET', 'POST'])
def spell_tooltip(spell_id):
    _, slots = logic.get_spell_tooltip(spell_id)
    return render_template('spell_tooltip.html', slots=slots)


@app.route("/about", methods=['GET'])
def about():
    with open(os.path.join(here, 'about.txt'), 'r') as fh:
        data = fh.read()
    return render_template('changelog.html', data=data)


@app.route("/changelog", methods=['GET'])
def changelog():
    with open(os.path.join(here, 'changelog.txt'), 'r') as fh:
        data = fh.read()
    return render_template('changelog.html', data=data)


@app.route("/error", methods=['GET'])
def error():
    return render_template('blank.html')


@app.route("/", methods=['GET'])
def main_page():
    return render_template('main.html')


@app.route("/debug/tester", methods=['GET'])
def tester():
    if SITE_TYPE != 'Development':
        flash("Unauthorized")
        return redirect(url_for('error'))
    # data, slots = logic._debugger()
    return render_template('blank.html')


@app.route("/item/detail/<int:item_id>")
def item_detail(item_id):
    data = logic.get_item_data(item_id, full=True)
    return render_template('item_detail.html', item=data)


@app.route("/item/raw/<int:item_id>")
def item_raw(item_id):
    raw_data = logic.get_item_raw_data(item_id)
    return render_template('raw_data.html', data=raw_data)


@app.route("/search/npc", methods=['GET', 'POST'])
def npc_search():
    if request.method == 'GET':
        return render_template('npc_search.html')
    else:
        npc_name = request.form['npc_name']
        if len(npc_name) > 50:
            flash('Search by name limited to 50 characters.')
            return redirect(url_for('npc_search'))
        elif len(npc_name) < 3:
            flash('Search by name requires at least 3 characters')
            return redirect(url_for('npc_search'))
        if not npc_name.isascii():
            flash('Only ASCII characters are allowed.')
            return redirect(url_for('npc_search'))
        data = logic.get_npcs(npc_name)
        return render_template('npc_search_result.html', data=data)


@app.route("/item/search", methods=['GET', 'POST'])
def item_fast_search():
    if request.method == 'GET':
        return render_template('item_fast_search.html')
    else:
        # Do some validation
        item_name = request.form.get('item_name')
        tradeskill = request.form.get('tradeskill')
        if tradeskill == 'none':
            tradeskill = None
        equippable = request.form.get('equippable')
        if equippable == 'none':
            equippable = None
        itype = request.form.get('itype')
        no_glamour = request.form.get('no_glamour')
        only_aug = request.form.get('only_aug')

        if len(item_name) > 50:
            flash('Search by name limited to 50 characters.')
            return redirect(url_for('item_fast_search'))
        if len(item_name) < 3:
            flash('Search by name requires at least 3 characters')
            return redirect(url_for('item_fast_search'))
        if not item_name.isascii():
            flash('Only ASCII characters are allowed.')
            return redirect(url_for('item_fast_search'))
        data = logic.get_fast_item(item_name, tradeskill=tradeskill, equippable=equippable,
                                   itype=itype, no_glamours=no_glamour, only_aug=only_aug)
        return render_template('item_fast_search_result.html', data=data)


@app.route("/search/spell", methods=['GET', 'POST'])
def spell_search():
    if request.method == 'GET':
        return render_template('spell_search.html')
    else:
        spell_name = request.form['spell_name']
        if len(spell_name) > 50:
            flash('Search by name limited to 50 characters.')
            return redirect(url_for('spell_search'))
        elif len(spell_name) < 3:
            flash('Search by name requires at least 3 characters')
            return redirect(url_for('spell_search'))
        if not spell_name.isascii():
            flash('Only ASCII characters are allowed.')
            return redirect(url_for('spell_search'))
        data = logic.get_spells(spell_name)
        return render_template('spell_search_result.html', data=data)


@app.route("/spell/detail/<int:spell_id>")
def spell_detail(spell_id):
    base_data, slots = logic.get_spell_data(spell_id)
    return render_template('spell_detail.html', data=base_data, slots=slots)


@app.route("/spell/raw/<int:spell_id>")
def spell_raw(spell_id):
    raw_data = logic.get_spell_raw_data(spell_id)
    return render_template('raw_data.html', data=raw_data)


@app.route("/search/item", methods=['POST'])
def item_search():
    # Do some validations
    filters = {}
    g_slot = None
    show_dmg_delay = False
    show_spells = False
    full_detail = False
    show_click = False
    show_proc = False
    data = request.form

    # Make sure _something_ was provided
    if (request.form['g_class_1'] == 'None' and
        request.form['g_class_2'] == 'None' and
        request.form['g_class_3'] == 'None' and
        request.form['g_slot'] == 'None' and
        request.form['i_type'] == 'None' and
        request.form['spell_type'] == '' and
        'pet_search' not in data):
        flash('Must request a slot, class, item type other than all, or focus effect, or select Search for Pet Items')
        return redirect(url_for('error'))

    if 'g_class_1' in request.form:
        filters.update({'g_class_1': request.form['g_class_1']})
    if 'g_class_2' in request.form:
        filters.update({'g_class_2': request.form['g_class_2']})
    if 'g_class_3' in request.form:
        filters.update({'g_class_3': request.form['g_class_3']})

    if 'g_slot' in request.form:
        if request.form['g_slot'] != 'None':
            filters.update({'g_slot': request.form['g_slot']})
            g_slot = request.form['g_slot']
            if 'Primary' in g_slot or 'Secondary' in g_slot or 'Range' in g_slot:
                show_dmg_delay = True

    # Handle Name
    if 'item_name' in request.form:
        if len(request.form['item_name']) > 0:
            filters.update({'item_name': request.form['item_name']})

    # Handle Item Type
    if request.form['i_type'] != 'None':
        i_type = request.form['i_type']

        # Do some validations here to stop insanity
        if g_slot is not None:
            # Handle Bows not in Range
            if 'Bow' in i_type and 'Range' not in g_slot:
                flash(f'Cannot search for item type "Bow" in slot {g_slot}')
                return redirect(url_for('error'))

            # Handle ranged with other weapon types
            if ('Bow' not in i_type and 'Any' not in i_type and 'Augment' not in i_type) and 'Range' in g_slot:
                flash(f'Range slot can only search for "Bow" or "Any"')
                return redirect(url_for('error'))

            # Handle Shield not in Secondary
            if 'Shield' in i_type and 'Secondary' not in g_slot and 'Back' not in g_slot:
                flash(f'Cannot search for item type "Shield" in slot {g_slot}')
                return redirect(url_for('error'))

            # Handle 2H not in Primary
            if (i_type in ['Two Hand Slash', 'Two Hand Blunt', 'Two Hand Piercing', 'Any 2H Weapon'] and
                    'Primary' not in g_slot):
                flash(f'Cannot search for Two-Handed items in slot {g_slot}')
                return redirect(url_for('error'))

            # Handle arrows in non-ammo slots
            if i_type == 'Arrow' and g_slot != 'Ammo':
                flash(f'Arrows can only go in the Ammo slot.')
                return redirect(url_for('error'))

            # Handle weapons in non-weapon slots
            if i_type not in ['Any', 'Shield', 'Bow', 'Augment', 'Arrow'] and g_slot not in ['Primary', 'Secondary']:
                flash(f'Cannot search for weapons in slot {g_slot}')
                return redirect(url_for('error'))

        filters.update({'i_type': i_type})

    # Handle Eras
    base_era_list = ['Classic', 'Kunark', 'Velious', 'Luclin', 'Planes']
    remove_era_list = request.form.getlist('eras')
    era_list = []
    for era in base_era_list:
        if era in remove_era_list:
            continue
        else:
            era_list.append(era)
    filters.update({'eras': era_list})

    # Handle Proc Weapon Items
    if 'proc' in data:
        if 'True' in data['proc']:
            if g_slot:
                if g_slot == 'Primary' or g_slot == 'Secondary' or g_slot == 'Range':
                    filters.update({'proc': True})
                    show_proc = True
                    if 'proc_level' in data:
                        if int(data['proc_level']) > 0:
                            filters.update({'proclevel2': data['proc_level']})

    # Handle Click Effect Items
    if 'click' in data:
        if 'True' in data['click']:
            filters.update({'click': True})
            show_click = True
            if 'click_level' in data:
                if int(data['click_level']) > 0:
                    filters.update({'clicklevel2': data['click_level']})

    # Handle Sympathetics
    if 'sympathetic' in data:
        if data['sympathetic'] != 'None':
            filters.update({'sympathetic': data['sympathetic']})
            show_click = True

    # Handle Stat Requirements
    reduce_changed = False
    reduce_restrictions = {
        'ac': False,
        'hp': False,
        'mana': False,
        'astr': False,
        'asta': False,
        'aagi': False,
        'adex': False,
        'awis': False,
        'aint': False,
        'acha': False,
        'heroic_str': False,
        'heroic_sta': False,
        'heroic_agi': False,
        'heroic_dex': False,
        'heroic_wis': False,
        'heroic_int': False,
        'heroic_cha': False,
        'fr': False,
        'cr': False,
        'pr': False,
        'dr': False,
        'mr': False,
        'attack': False,
        'haste': False,
        'regen': False,
        'manaregen': False,
        'spelldmg': False,
        'healamt': False,
        'accuracy': False,
        'avoidance': False,
        'combateffects': False,
        'damageshield': False,
        'dotshielding': False,
        'shielding': False,
        'spellshield': False,
        'strikethrough': False,
        'stunresist': False,
    }
    for i in range(1, 100):
        thing = 'stat_%s' % (i)
        thing_val = 'stat_val_%s' % (i)
        if thing in request.form:
            if request.form[thing] in filters:
                flash('Cannot add the same item stat filter twice.')
                return redirect(url_for('error'))
            if 'none' in request.form[thing]:
                continue

            filters.update({
                request.form[thing]: float(request.form[thing_val])})
            if 'reduce_restrict' in request.form:
                reduce_changed = True
                reduce_restrictions.update({request.form[thing]: True})
        else:
            continue

    # Handle Weights
    show_values = False
    weights = {}
    for i in range(1, 100):
        thing = 'weight_%s' % (i)
        thing_val = 'stat_weight_%s' % (i)
        if thing in request.form:
            show_values = True
            if request.form[thing] in weights:
                flash('Cannot add the same item stat weight twice.')
                return redirect(url_for('error'))
            if 'none' in request.form[thing]:
                continue
            weights.update({
                request.form[thing]: float(request.form[thing_val])})
            if 'show_weight_detail' in request.form:
                reduce_changed = True
                reduce_restrictions.update({request.form[thing]: True})
        else:
            continue

    # Handle Show Table
    if 'show_full_detail' in request.form:
        full_detail = True

    if not reduce_changed:
        # Flip them all to true
        for entry in reduce_restrictions:
            reduce_restrictions[entry] = True

    # Handle Ignore Zero
    if 'ignore_zero' in request.form:
        if not show_values:
            flash('Include zero weight items requires at least one weight.')
            return redirect(url_for('error'))
        ignore_zero = False
    else:
        ignore_zero = True

    # Handle no rent
    if 'pet_search' in request.form:
        filters.update({'pet_search': True})

    # Handle focus effects
    if 'spell_type' in request.form:
        if request.form['spell_type'] is not None and request.form['spell_type'] != '':
            filters.update({'focus_type': request.form['spell_type']})
            filters.update({'sub_type': request.form['focus_type']})
            show_spells = True

    # Handle elem damage
    if 'elemdmgtype' in data:
        if g_slot:
            if g_slot == 'Primary' or g_slot == 'Secondary' or g_slot == 'Range':
                if data['elemdmgtype'] != 'all':
                    filters.update({'elemdmgtype': data['elemdmgtype']})

    # Handle bane damage
    if 'banetype' in data:
        if g_slot:
            if g_slot == 'Primary' or g_slot == 'Secondary' or g_slot == 'Range':
                if data['banetype'] != 'all':
                    bane_id = int(data['banetype'].split('_')[1])
                    if 'body' in data['banetype']:
                        filters.update({'banedmgbody': bane_id})
                    else:
                        filters.update({'banedmgrace': bane_id})

    # Oh god, we've got everything...lets get a list of items
    ret_items, focus, worn, inst = logic.get_items_with_filters(weights, ignore_zero, **filters)
    return render_template('item_search_results.html', data=ret_items, reduce=reduce_restrictions,
                           show_dmg_delay=show_dmg_delay, show_focus=focus, full_detail=full_detail,
                           show_values=show_values, show_click=show_click, show_proc=show_proc, show_worn=worn,
                           show_inst=inst, show_spells=show_spells)


@app.route("/search/weapon", methods=['GET', 'POST'])
def weapon_search():
    if request.method == 'GET':
        return render_template('weapon_search.html')
    else:
        return redirect(url_for('item_search'), code=307)


@app.route("/search/armor", methods=['GET', 'POST'])
def armor_search():
    if request.method == 'GET':
        return render_template('item_search.html')
    else:
        return redirect(url_for('item_search'), code=307)


@app.route("/report/<item_id>", methods=['GET', 'POST'])
def report_item(item_id):
    if request.method == 'GET':
        return render_template('item_report.html', item=logic.get_item_data(item_id))


if __name__ == "__main__":
    app.debug = True
    app.run(port=5001)
