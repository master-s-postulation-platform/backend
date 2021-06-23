from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import serializers, status, authentication, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
# Django
from django.http import Http404
# Serializers
from .serializers import ( 
                            CambridgeLevelSerializer, ExperienceSerializer, 
                            FisrtPageProfileSerializer, SecondPageProfileSerializer, 
                            EducationSerializer, LanguagesSerializer,
                            CitiesSerializer, CountriesSerializer,
                            GottenGradeSerializer, LastGradeSerializer,
                            CivilStatusSerializer, CambridgeLevel,
                        )
# Models
from .models import (
                        Cities, CivilStatus, 
                        Countries, Education, 
                        GottenGrade, LastGrade, 
                        Profile, ProfessionalExperience, 
                        Languages,
                    )
"""Endpoint education [POST, GET]:
   GET: Give a response with all education that match with an user-profile
   POST: Create a new row with education into user-profile
        Response: The Education info that was created"""
class education_profile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        try:
            profile = Profile.objects.get(user=request.user.id)
            education_obj = Education.objects.get(pk=pk)
            if education_obj.profile == profile:
                return education_obj
            raise Http404
        except:
            raise Http404

    def get(self, request):
        try:
            profile = Profile.objects.filter(user=request.user.id)
            education_serializer = EducationSerializer(Education.objects.filter(profile=profile[0].id), many=True)
        except:
            # return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)
            raise Http404

        return Response(education_serializer.data)
    
    def post(self, request):
        education_serializer = EducationSerializer(data=request.data)
        if education_serializer.is_valid():
            response = education_serializer.create(request)
            if response :
                education_response = EducationSerializer(response)
                return Response(education_response.data, status=status.HTTP_201_CREATED)
            # return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)
            raise Http404
        return Response(education_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
            education_item = self.get_object(request, request.data.get('education_id'))
            education_serializer = EducationSerializer(education_item, data=request.data)
            if education_serializer.is_valid():
                education_response = education_serializer.update(education_item, request.data)
                if education_response:
                    response = EducationSerializer(education_response)
                    return Response(response.data)
                raise Http404
            return Response(education_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        education_item = self.get_object(request, request.data.get('education_id'))
        education_item.delete()
        return Response({"delete":"done"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def profile_form(request, page):
    
    countries_serializer = CountriesSerializer(Countries.objects.all(), many=True)
   
    if page == 1:
        
        civil_status_serializer = CivilStatusSerializer(CivilStatus.objects.all(), many=True)
        options = {
            "countries": countries_serializer.data,
            "civil_status": civil_status_serializer.data,
        }
        profile = Profile.objects.filter(user=request.user.id)
        serializer = FisrtPageProfileSerializer(profile, many=True)

        return Response({
                            "profile": serializer.data,
                            "options": options,
                        })
    if page == 2:
        
        profile = Profile.objects.filter(user=request.user.id)
        profile_serializer = SecondPageProfileSerializer(profile, many=True)

        gotten_grade_serializer = GottenGradeSerializer(GottenGrade.objects.all(), many=True)

        last_grade_serializer = LastGradeSerializer(LastGrade.objects.all(), many=True)

        cities_serializer = CitiesSerializer(Cities.objects.all(), many=True)

        canbridge_level_serializer = CambridgeLevelSerializer(CambridgeLevel.objects.all(), many=True)

        options = {
            "cities": cities_serializer.data,
            "countries": countries_serializer.data,
            "last_grade": last_grade_serializer.data,
            "gotten_grade": gotten_grade_serializer.data,
            "cambridge_level": canbridge_level_serializer.data,
        }

        return Response({
                            "profile": profile_serializer.data, 
                            "options": options,
                        })
    else:
        return Response({"response": "page not found"}, status=404)