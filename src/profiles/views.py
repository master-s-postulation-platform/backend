from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import serializers, status, authentication, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
# Django
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
# Serializers
from .serializers import ( 
                            AddressSerializer, CambridgeLevelSerializer, ExperienceSerializer, 
                            FisrtPageProfileSerializer, SecondPageProfileSerializer, 
                            EducationSerializer, LanguagesSerializer,
                            CitiesSerializer, CountriesSerializer,
                            GottenGradeSerializer, LastGradeSerializer,
                            CivilStatusSerializer, CambridgeLevel,
                            ProfileSerializer, UserSerializer,
                        )
# Models
from .models import (
                        Address, Cities, CivilStatus, 
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


class LanguageProfile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.filter(user=request.user.id)
            language_serializer = LanguagesSerializer(Languages.objects.filter(profile=profile[0].id), many=True)
        except:
            return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(language_serializer.data)

    def post(self, request):
        language_serializer = LanguagesSerializer(data=request.data)
        if language_serializer.is_valid():
            response = language_serializer.create(request)
            if response:
                language_response = LanguagesSerializer(response)
                return Response(language_response.data, status=status.HTTP_201_CREATED)
            return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(language_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        language_serializer = LanguagesSerializer(Languages, data=request.data)
        if language_serializer.is_valid():
            language_serializer.save()
            return Response(language_serializer.data, status=status.HTTP_200_OK)
        return Response(language_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExperienceProfile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.filter(user=request.user.id)
            experience_serializer = ExperienceSerializer(ProfessionalExperience.objects.filter(profile=profile[0].id),
                                                         many=True)
        except:
            return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(experience_serializer.data)

    def post(self, request):
        experience_serializer = ExperienceSerializer(data=request.data)
        if experience_serializer.is_valid():
            response = experience_serializer.create(request)
            if response:
                experience_response = ExperienceSerializer(response)
                return Response(experience_response.data, status=status.HTTP_201_CREATED)
            return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(experience_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        experience_serializer = ExperienceSerializer(ProfessionalExperience, data=request.data)
        if experience_serializer.is_valid():
            experience_serializer.save()
            return Response(experience_serializer.data, status=status.HTTP_200_OK)
        return Response(experience_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        education = Education.objects.filter(user=request.user.id)
        education.delete()


@api_view(['GET', 'POST', 'PUT'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def profile_form(request, page):

    if request.method == 'GET':

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

    elif request.method == 'PUT':

        if page == 1:
            profile = Profile.objects.get(user=request.user.id)
            user = request.user
            data = request.data

            user_data = {
                "email": user.email,
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "username": data.get("username")
            }
            try:
                profile_data = {
                    "user":user,
                    "birthday": data.get("birthday"),
                    "civil_status": CivilStatus.objects.get(pk= data.get("c_status")),
                    "home_phone": data.get("home_phone"),
                    "mobile_phone": data.get("mobile_phone")
                }
                address_data = {
                    "country":Countries.objects.get(pk=data.get("country")),
                    "city": Cities.objects.get(pk=data.get("city")),
                    "address_line1": data.get("address_line1")
                }
            except ObjectDoesNotExist:
                return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)

            address_item = profile.Address
            if address_item is None:
                address_item = Address.objects.create()
                profile_data['Address'] = address_item       
            address_serializer = AddressSerializer(address_item, data=address_data)
            if address_serializer.is_valid():
                address_serializer.update(address_item, address_data)
            else:
                return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


            user_serializer = UserSerializer(user, data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            profile_serializer = ProfileSerializer(profile, data=profile_data)
            if profile_serializer.is_valid():
                profile_response = profile_serializer.update(profile, profile_data)
                if profile_response:
                    response = FisrtPageProfileSerializer(profile_response)
                    return Response(response.data)
                raise Http404
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if page == 2:
            profile_serializer = SecondPageProfileSerializer(data=request.data)
            if profile_serializer.is_valid():
                response = profile_serializer.create(request)
                if response:
                    profile_response = SecondPageProfileSerializer(response)
                    return Response(profile_response.data, status=status.HTTP_201_CREATED)
                return Response({"error": "Server error"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
