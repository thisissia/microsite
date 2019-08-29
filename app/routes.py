from app import app, db
from app.forms import Name, Uploads, Testing, Update, Update2, filesType
from flask import render_template, flash, redirect, session, url_for, request
from app.models import Classifier, Conversation
from app.aux_functions import xlsxparser, worker
import threading, queue, pandas as pd, json


@app.route('/')
@app.route('/index')
def index():
    # try:
    #     db.session.query(Conversation).all()
    #     flash('worked')
    # except Exception as e:
    #     db.create_all()
    #     flash(e)
    session['classif_name'] = None
    return render_template('index.html', title='Home')


@app.route('/specificClassifier/name', methods=['GET', 'POST'])
def name():
    form = Name()
    if form.validate_on_submit():
        name = Classifier.query.filter_by(name=form.name.data).first()
        if name is None:
            flash('Model not found - please try again')
            return render_template('specificClassifier/name.html', title='Classify using specific classifier', form=form)
        else:
            session['classif_name'] = form.name.data
            return redirect("/testing")
    return render_template('specificClassifier/name.html', title='Classify using specific classifier', form=form)


@app.route('/testing', methods=['GET', 'POST'])
def testing():
    form = Testing()
    name = session['classif_name']
    if form.validate_on_submit():
        try:
            df = pd.read_excel(form.files.data, header=[0, 1])
            gap, duration, ts, te, si = xlsxparser(df)
            file_name = df.columns.levels[0].values

            conversations_good = Conversation.query.filter_by(model=session['classif_name'], types=True).all()
            conversations_bad = Conversation.query.filter_by(model=session['classif_name'], types=False).all()

            gap_g = []
            duration_g = []
            for convo in conversations_good:
                gap_g.append(convo.data['Gap'])
                duration_g.append(convo.data['Duration'])

            gap_b = []
            duration_b = []
            for convo in conversations_bad:
                gap_b.append(convo.data['Gap'])
                duration_b.append(convo.data['Duration'])

            prior = 1
            q = queue.Queue()
            results = {}
            threads = []

            for i, v in enumerate(file_name):
                thread = threading.Thread(target=worker(gap_g, gap_b, duration_g, duration_b,
                                                        gap[i], duration[i], prior, i, q))
                threads.append(thread)
                thread.start()

            for x in threads:
                x.join()

            while not q.empty():
                i, v = q.get()
                results[i] = v

            df = pd.DataFrame(columns=['No.', 'Name', 'Result'])
            for key, value in results.items():
                if value:
                    temp = 'Good'
                else:
                    temp = 'Bad'

                df.loc[key] = [key, file_name[key], temp]
            return redirect(url_for('.results', df = df.to_html()))
        except Exception as e:
            flash(f'The file(s) uploaded were not excel files or {e}')
    return render_template('testing.html', title='Test your files with the classifier', form=form, name=name)


@app.route('/newClassifier', methods=['GET', 'POST'])
def newClassifier():
    form = Uploads()

    if form.validate_on_submit():
        try:
            g_df = pd.read_excel(form.good.data, header=[0,1])
            b_df = pd.read_excel(form.bad.data, header=[0,1])

            newModel = Classifier(name=form.name.data)
            db.session.add(newModel)
            session['classif_name'] = form.name.data

            gaps_good, duration_good, ts_g, te_g, si_g = xlsxparser(g_df)
            gaps_bad, duration_bad, ts, te, si = xlsxparser(b_df)
            file_name_g = g_df.columns.levels[0].values
            file_name_b = b_df.columns.levels[0].values

            for i, v in enumerate(duration_bad):
                newConversation = Conversation(file_name=str(file_name_b[i]), types=False,
                                               data={'Duration': v, 'Gap': gaps_bad[i],
                                                     'Time_start': ts[i], 'Time_end': te[i],
                                                     'Speaker_id': si[i]}, model=form.name.data)
                db.session.add(newConversation)

            for i, v in enumerate(duration_good):
                print(i)
                newConversation = Conversation(file_name=str(file_name_g[i]), types=True,
                                               data={'Duration': v, 'Gap': gaps_good[i],
                                                     'Time_start': ts_g[i], 'Time_end': te_g[i],
                                                     'Speaker_id': si_g[i]}, model=form.name.data)
                db.session.add(newConversation)

            db.session.commit()
            flash('Model has been created!')
            flash('Conversations has been added to the database.')
            return redirect("/testing")
        except Exception as e:
            flash(f'The file(s) uploaded were not excel files or {e}')
    return render_template('uploads.html', title='Make a new classifier!', form=form)


@app.route('/genericClassifier', methods=['GET', 'POST'])
def genClassifier():
    session['classif_name'] = 'gen'
    return redirect("/testing")


@app.route("/results", methods=['GET', 'POST'])
def results():
    df_html = request.args['df']
    return render_template('results.html', table_html=df_html)


@app.route('/specificClassifier/update', methods=['GET', 'POST'])
def update():
    form = Update()
    if form.validate_on_submit():
        session['classif_name'] = form.name.data
        df = pd.read_excel(form.files.data, header=[0, 1])
        file_names = df.columns.levels[0].values
        gaps, duration, ts, te, si = xlsxparser(df)
        data = {'file_name':[]}
        db.session.begin_nested()
        for i, v in enumerate(file_names):
            convo = Conversation()
            save_conversation(convo, [str(v), None, form.name.data,
                                      {'Duration': duration[i], 'Gap': gaps[i], 'Time_start': ts[i],
                                       'Time_end': te[i], 'Speaker_id': si[i]}], new=True)
            data['file_name'].append(str(v))
        return redirect(url_for('.labelConversations', data=json.dumps(data)))
    return render_template('specificClassifier/update.html', form=form)


@app.route('/labelConversations', methods=['GET', 'POST'])
def labelConversations():
    data = json.loads(request.args['data'])['file_name']
    form = Update2()
    for file_name in data:
        second_form = filesType()
        second_form.file_name = file_name
        form.files.append_entry(second_form)
    try:
        if request.method == 'POST':
            if request.form['edit'] == 'Update!':
                for files in form.files:
                    conversation = Conversation.query.filter_by(model=session['classif_name'], types=None,
                                                                file_name=files.file_name.data).first()
                    conversation.types = bool(files.types.data)
                if Conversation.query.filter_by(model=session['classif_name'], types=None).first() is not None:
                    conversation = db.session.query(Conversation).filter(Conversation.model == session['classif_name'],
                                                                         Conversation.types == None).all()
                    for convo in conversation:
                        db.session.delete(convo)
                db.session.commit()
                flash('Conversations added to the database')
                return redirect('/index')

            else:
                conversation = db.session.query(Conversation).filter(Conversation.model == session['classif_name'],
                                                                     Conversation.types == None).all()
                for convo in conversation:
                    db.session.delete(convo)
                db.session.commit()
                flash('Conversations where not added to the database')
                return redirect('/index')

    except Exception as err:
        conversation = db.session.query(Conversation).filter(Conversation.model == session['classif_name'],
                                                             Conversation.types == None).all()
        for convo in conversation:
            db.session.delete(convo)
        db.session.commit()
        flash(err)
        return redirect('/index')
    return render_template('specificClassifier/label.html', form=form)

def save_conversation(conversation, details, new=False):
    conversation.file_name = details[0]
    conversation.types = details[1]
    conversation.model = details[2]
    if details[3]:
        conversation.data = details[3]
    if new:
        db.session.add(conversation)
    db.session.commit()
