import pandas as pd
import datetime
import math
import os

# Django
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model

# Rest_framework
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework import serializers, status, authentication, permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# Utilities
from utils.dataframe_to_excel import Dataframe2Excel
from utils.constants import CONSTANTS
from utils.responses import Responses

# Reportlab
from reportlab.platypus import Paragraph, Table, TableStyle, Image, BaseDocTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO

# Models
from profiles.models import Profile
from .models import Score

# Serializers
from .serializers import CandidatesListSerializer, CandidateDetailSerializer, AdminDetailSerializer, ScoreSerializer
from profiles.serializers import UserSerializer

User = get_user_model()


class UpdateScore(UpdateAPIView):
    """Update the score of a candidate's profile"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer

    def put(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            profile_obj = Profile.objects.get(pk=request.data.get('profile_id'))
            if instance.id == profile_obj.score.id:
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                if serializer.is_valid():
                    response = serializer.save()
                    response = ScoreSerializer(response)
                    return Responses.make_response(data=response.data, authorization=True)
                    # return self.update(request, *args, **kwargs)
            raise Exception
        except:
            return Responses.make_response(error=True, message="Server error", 
                                           status=status.HTTP_500_INTERNAL_SERVER_ERROR, authorization=True)


class GetCandidateDetails(RetrieveUpdateAPIView):
    """Get the Profile detail of an Candidate user"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = CandidateDetailSerializer
    lookup_field = 'user'
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        new_object = self.get_object()
        serializer = CandidateDetailSerializer(new_object)
        return Responses.make_response(data=serializer.data, authorization=True)


class GetAdminDetails(RetrieveUpdateAPIView):
    """Get the User detail of an Admin user"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminDetailSerializer
    queryset = User.objects.filter(is_staff=True)

    def get(self, request, *args, **kwargs):
        new_object = self.get_object()
        serializer = AdminDetailSerializer(new_object)
        return Responses.make_response(data=serializer.data, authorization=True)



class AdministratorsView(ListAPIView):
    """Get the list of administrators"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.filter(is_staff=True)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        total_administrators = queryset.count()
        data = {
            "count": total_administrators,
            "data": serializer.data
        }
        return Responses.make_response(data=data, authorization=True)



@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def candidates_view(request):
    ITEMS_PER_PAGE = 2
    items_per_page = ITEMS_PER_PAGE
    page_num = request.query_params.get('page')
    items_pp_query = request.query_params.get('ippage')
    sort_option = request.query_params.get('sort')
    format_export = request.query_params.get('2xlsx')
    order = 'total_score'

    if sort_option == 'desc':
        order = '-total_score'

    try:
        if items_pp_query is not None:
            items_per_page = items_pp_query

        profile_list = Profile.objects.order_by(order)
        total_candidates = profile_list.count()
        admin_list = User.objects.filter(is_staff=True)
        admin_count = admin_list.count()
        candidate_count = total_candidates
        total_users = total_candidates + admin_count

        # Getting ready the data to export to excel format, only if param '2xlsx' is equal to '1'.
        if format_export == '1':

            users_count = {
                'User type': ['Admin', 'Candidate'],
                'Count': [admin_count, candidate_count]
            }

            candidate_obj = {
                'username': [],
                'email': [],
                'Name': [],
                'Location': [],
                'score': [],
                'total_score': []
            }

            for candidate in profile_list:
                candidate_obj['username'].append(candidate.user.username)
                candidate_obj['email'].append(candidate.user.email)
                candidate_obj['Name'].append(candidate.user.first_name)
                candidate_obj['Location'].append(candidate.Address)
                candidate_obj['score'].append(candidate.score)
                candidate_obj['total_score'].append(candidate.total_score)

            admin_obj = {
                'email': [],
                'First_name': [],
                'Last_name': []
            }

            for admin in admin_list:
                admin_obj['email'].append(admin.email)
                admin_obj['First_name'].append(admin.first_name)
                admin_obj['Last_name'].append(admin.last_name)

            # profile_list_df = pd.DataFrame(profile_list.values())
            profile_list_df = pd.DataFrame.from_dict(candidate_obj)
            admin_list_df = pd.DataFrame.from_dict(admin_obj)
            count_users_df = pd.DataFrame.from_dict(users_count)

            data = {
                "candidate": profile_list_df,
                "admin": admin_list_df,
                "count": count_users_df,
            }

            return Dataframe2Excel.df2xlsx(data=data, name='Report_Up_Program')
            # profile_list_df.to_excel("output.xlsx")

        # Getting ready the data to export to PDF format, only if param '2xlsx' is equal to '2'.
        elif format_export == '2':

            current_date = datetime.date.today().strftime('%d/%m/%Y')
            buffer = BytesIO()

            # Create the PDF object, using the buffer as its "file."
            p = canvas.Canvas(buffer, pagesize=A4)

            # Draw things on the PDF. Here's where the PDF generation happens.
            p.setLineWidth(.2)
            p.setFont('Helvetica', 22)
            p.drawString(30, 750, 'PPM')

            p.setFont('Helvetica', 12)
            p.drawString(30, 735, 'Report')

            high = 550

            p.setFont('Helvetica', 12)
            p.drawString(30, 685, f'Numero total de candidatos : {total_candidates}')
            p.drawString(30, 670, f'Numero total de administradores : {admin_count}')
            p.drawString(30, 655, f'Numero total de usuarios : {total_users}')
            p.setFont('Helvetica-Bold', 12)
            p.drawString(240, 600, f'Lista de postulantes ')

            p.setFont('Helvetica-Bold', 12)
            p.drawString(480, 750, current_date)
            p.line(460, 747, 560, 747)

            # Table header
            styles = getSampleStyleSheet()
            styleBH = styles['Normal']
            styleBH.alignment = TA_CENTER
            styleBH.fontSize = 10

            id_candidate = Paragraph('''Id''', styleBH)
            username = Paragraph('''Username''', styleBH)
            email = Paragraph('''Email''', styleBH)
            name = Paragraph('''Name''', styleBH)
            location = Paragraph('''Location''', styleBH)
            total_score = Paragraph('''Total Score''', styleBH)

            data_user = [[id_candidate, username, email, name, location, total_score]]

            # table
            styleN = styles['BodyText']
            styleN.alignment = TA_CENTER
            styleN.fontSize = 7

            for candidate in profile_list:
                this_candidate = [candidate.user.id,
                                  candidate.user.username,
                                  candidate.user.email,
                                  candidate.user.first_name,
                                  candidate.Address,
                                  candidate.total_score
                                  ]

                data_user.append(this_candidate)
                high -= 18
            p.showPage()

            email = Paragraph('''Email''', styleBH)
            First_name = Paragraph('''First Name''', styleBH)
            Last_name = Paragraph('''Last Name''', styleBH)

            data_admin = [[email, First_name, Last_name]]

            high2 = high - 100

            p.setFont('Helvetica-Bold', 12)
            p.drawString(230, high2 + 45, f'Lista de administradores ')

            for admin in admin_list:
                this_admin = [admin.email,
                              admin.first_name,
                              admin.last_name
                              ]
                data_admin.append(this_admin)
                high2 -= 18

            # table size

            width, height = A4
            table = Table(data_user, colWidths=[1.0 * cm, 3.3 * cm, 4.0 * cm, 3.0 * cm, 5.0 * cm, 2.3 * cm])
            table.setStyle(TableStyle([
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]))

            width, height = A4
            table2 = Table(data_admin, colWidths=[6.2 * cm, 6.2 * cm, 6.2 * cm])
            table2.setStyle(TableStyle([
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]))

            # pdf size

            table2.wrapOn(p, width, height)
            table2.drawOn(p, 30, high2)

            table.wrapOn(p, width, height)
            table.drawOn(p, 30, high)

            # Close the PDF object cleanly, and we're done.
            p.showPage()
            p.save()

            # FileResponse sets the Content-Disposition header so that browsers
            # present the option to save the file.
            buffer.seek(0)

            return FileResponse(buffer, as_attachment=True, filename='Report_Up_Program.pdf')

        paginator = Paginator(profile_list, items_per_page)
        try:
            profile_list = paginator.page(page_num)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            profile_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            profile_list = paginator.page(paginator.num_pages)
        data_serializer = CandidatesListSerializer(profile_list, many=True)
        total_pages = math.ceil(total_candidates / int(items_per_page))
        data = {
            "pages": total_pages,
            "count": total_candidates,
            "data": data_serializer.data
        }
        return Responses.make_response(data=data)
    except ValueError:
        return Responses.make_response(error=True,
                                       message=CONSTANTS.get('error_server'),
                                       status=status.HTTP_400_BAD_REQUEST, authorization=True)
