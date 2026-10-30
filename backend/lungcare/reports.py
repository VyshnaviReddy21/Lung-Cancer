from html import escape
import uuid
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from flask import current_app
from .security import db,now
from .workflows import notify,audit
DISCLAIMER = 'ACADEMIC DEMONSTRATION — NOT A CLINICAL DIAGNOSTIC REPORT'
def generate_report(case):
    database = db(); prediction = database.predictions.find_one({'case_id':case['_id']})
    if not prediction: raise ValueError('A successful saved prediction is required.')
    review = database.doctor_reviews.find_one({'case_id':case['_id']})
    styles = getSampleStyleSheet(); case_id = str(case['_id']); directory = current_app.config['REPORT_DIRECTORY']
    path = directory / f'{case_id}.pdf'; temp = directory / f'{case_id}.{uuid.uuid4().hex}.tmp.pdf'
    story = [Paragraph('LungCare AI',styles['Title']),Paragraph(DISCLAIMER,styles['Heading2']),Spacer(1,16)]
    def line(key,value): story.extend([Paragraph(f'<b>{escape(key)}:</b> {escape(str(value))}',styles['BodyText']),Spacer(1,8)])
    line('Case ID',case_id);line('Patient identifier',case['patient_id']);line('Upload date · UTC',case['created_at']);line('Analysis date · UTC',prediction['created_at']);line('AI-assisted finding',prediction['label']);line('Confidence',f"{prediction['confidence']*100:.2f}%");line('Model version',prediction['model_version'])
    data = [['Classification','Probability']]+[[key,f'{value*100:.2f}%'] for key,value in prediction['probabilities'].items()]
    table = Table(data,colWidths=[330,130]);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EDF4FC')),('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor('#17365D')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#E2E8F0')),('BOTTOMPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),10)]));story += [table,Spacer(1,16)]
    line('Grad-CAM',prediction.get('gradcam_reason','Unavailable'))
    if review:
        doctor=database.users.find_one({'_id':review['doctor_id']});line('Demo doctor',doctor['full_name'] if doctor else 'Demonstration doctor');line('Decision',review['decision']);line('Assessment',review['assessment']);line('Optional notes',review.get('notes',''));line('Review date · UTC',review['created_at'])
    else: line('Academic review','Not yet completed')
    story += [Spacer(1,20),Paragraph('Model explanations are not proof of cancer. Consult a qualified medical professional. This academic prototype has not established clinical validity.',styles['BodyText'])]
    SimpleDocTemplate(str(temp)).build(story);temp.replace(path)
    database.reports.update_one({'case_id':case['_id']},{'$set':{'patient_id':case['patient_id'],'path':str(path),'created_at':now()}},upsert=True)
    notify(database,case['patient_id'],'Your academic PDF report is available.',case['_id']);audit(database,'report_generated',case['_id'])
    return path
