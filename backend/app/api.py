from rest_framework import viewsets
from rest_framework.response import Response
from permissions.clerk import ClerkAuthenticated
from .models import ConnectedSocialMedia, ProductListings
from rest_framework.views import APIView
from .serializers import ConnectedSocialMediaSerializer, ProductListingsSerializer
from .Social2Amazon import Social2Amazon
from .InstaFetcher import InstaFetcher
from .FacebookFetcher import FacebookFetcher
from .VideoFrameExtractor import VideoFrameExtractor
from .ImageQualityChecker import ImageQualityChecker
import backend.settings as settings
from rest_framework.permissions import AllowAny

post_data = [
    {
        "id": 1,
        "title": "Travelling to Dubai",
        "description": "It was an amazing trip"
    }
]

class PostViewset(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    permission_classes = [ClerkAuthenticated]
    def list(self, request):
        return Response(post_data)

class ConnectedSocialMediaAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def get(self, request):
        connected_social_media = ConnectedSocialMedia.objects.first()
        serializer = ConnectedSocialMediaSerializer(connected_social_media)
        return Response(serializer.data)

class UpdateConnectedSocialMediaAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def post(self, request):
        data = request.data
        connected_social_media = ConnectedSocialMedia.objects.first()
        instagram_link = data.get('instagram_link', '')
        facebook_link = data.get('facebook_link', '')
        tiktok_link = data.get('tiktok_link', '')
        if not connected_social_media:
            connected_social_media = ConnectedSocialMedia(instagram_link=instagram_link, facebook_link=facebook_link, tiktok_link=tiktok_link)
            connected_social_media.save()
            return Response(connected_social_media)
        else:
            if instagram_link != '':
                connected_social_media.instagram_link = instagram_link
            if facebook_link != '':
                connected_social_media.facebook_link = facebook_link
            if tiktok_link != '':
                connected_social_media.tiktok_link = tiktok_link
            connected_social_media.save()

        serializer = ConnectedSocialMediaSerializer(connected_social_media)
        return Response(serializer.data)

class RecentFetchedPostAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def get(self, request):
        """
        Get the most recent fetched post, only 1 post
        """
        recent_fetched_posts = ProductListings.objects.last()
        
        if recent_fetched_posts:
            # Get serialized data
            serializer = ProductListingsSerializer(recent_fetched_posts)
            data = serializer.data
            
            # Update image URLs to include full domain if needed
            if 'images_list' in data and data['images_list']:
                data['full_images_list'] = recent_fetched_posts.get_full_image_urls()
                
            return Response(data)
        
        return Response({})

class UpdateListingAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def post(self, request):
        data = request.data
        product_id = data.get('product_id')
        product = ProductListings.objects.get(product_id=product_id)
        product.images_list = data.get('images_list')
        product.product_title = data.get('product_title')
        product.price = data.get('price')
        product.product_details = data.get('product_details')
        product.about_this_item = data.get('about_this_item')
        product.product_description = data.get('product_description')
        product.approved = data.get('approved')
        product.save()
        serializer = ProductListingsSerializer(product)
        return Response(serializer.data)

class PreviousListingAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def get(self, request):
        # Change: Get ALL listings instead of excluding the most recent
        # Previously this was using [1:] which skipped the first result
        all_listings = ProductListings.objects.all().order_by('-created_at')
        serializer = ProductListingsSerializer(all_listings, many=True)
        return Response(serializer.data)

class DashboardStatsAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def get(self, request):
        total_products = ProductListings.objects.count()
        approved_products = ProductListings.objects.filter(approved=True).count()
        disapproved_products = ProductListings.objects.filter(approved=False).count()
        
        total_connected_social_media = ConnectedSocialMedia.objects.first()
        connected_social_media_count = 0

        if total_connected_social_media:
            links = [
                total_connected_social_media.instagram_link,
                total_connected_social_media.facebook_link,
                total_connected_social_media.tiktok_link,
            ]
            connected_social_media_count = sum(1 for link in links if link.strip())

        return Response({
            "total_listings": total_products,
            "approved_listings": approved_products,
            "disapproved_listings": disapproved_products,
            "connected_social_media": connected_social_media_count
        })

class ProfileDataAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def get(self, request):
        first_name = request.clerk_user['data'].get('first_name')
        profile_image = request.clerk_user['data'].get('image_url')
        return Response({
            "first_name": first_name,
            "profile_image": profile_image
        })

class FetchInstagramPostAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def get(self, request):
        total_connected_social_media = ConnectedSocialMedia.objects.first()
        if not total_connected_social_media:
            return Response({
                "message": "Please connect your social media accounts"
            })
        else:
            instagram_link = total_connected_social_media.instagram_link
            if not instagram_link:
                return Response({
                    "message": "Please provide a valid Instagram username"
                })
            else:
                username = instagram_link.split(".com/")[1].strip()

                if not username:
                    return Response({
                        "message": "Please provide a valid Instagram username"
                    })
                else:
                    RAPIDAPI_KEY = settings.RAPIDAPI_KEY
                    fetcher = InstaFetcher(RAPIDAPI_KEY)
                    post_links = fetcher.get_user_posts(username)
                    return Response({
                        "message": "Posts fetched successfully",
                        "post_links": post_links
                    })

class FetchFaceBookPostAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def get(self, request):
        total_connected_social_media = ConnectedSocialMedia.objects.first()
        if not total_connected_social_media:
            return Response({
                "message": "Please connect your social media accounts"
            })
        else:
            facebook_link = total_connected_social_media.facebook_link
            if not facebook_link:
                return Response({
                    "message": "Please provide a valid Facebook username"
                })
            else:
                username = facebook_link.split(".com/")[1].strip()

                if not username:
                    return Response({
                        "message": "Please provide a valid Facebook username"
                    })
                else:
                    FACEBOOK_RAPIDAPI_KEY = settings.FACEBOOK_RAPIDAPI_KEY
                    scraper = FacebookFetcher(FACEBOOK_RAPIDAPI_KEY)
                    posts = scraper.fetch_posts_from_profile(facebook_link)
                    if posts:
                        return Response({
                            "message": "Posts fetched successfully",
                            "post_links": posts
                        })
                    else: 
                        return Response({
                            "message": "Failed to fetch posts"
                        })

class ConvertVideoToImagesAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def post(self, request):
        video_url = request.data.get('video_url', '')
        if not video_url:
            return Response({
                "message": "Please provide a valid video URL"
            })
        else:
            extractor = VideoFrameExtractor(video_url)
            try:
                frame_files = extractor.extract_frames()
                
                # Ensure frame_files have full URLs with domain
                full_frame_urls = []
                base_url = "http://127.0.0.1:8000" if settings.DEBUG else ""
                
                for url in frame_files:
                    # Make sure we have a proper URL format
                    if url.startswith('/'):
                        url = f"{base_url}{url}"
                    elif not url.startswith('http') and settings.DEBUG:
                        url = f"{base_url}/{url}"
                    full_frame_urls.append(url)
                
                get_quality = ImageQualityChecker(full_frame_urls)
                quality_images = get_quality.start()
                
                return Response({
                    "message": "Video converted to images successfully",
                    "quality_images": quality_images
                })
            except Exception as e:
                # Add error handling to help debug issues
                import traceback
                print(f"Error extracting frames: {str(e)}")
                print(traceback.format_exc())
                return Response({
                    "message": f"Error extracting frames: {str(e)}",
                    "error": True
                }, status=500)

class Social2AmazonAPI(APIView):
    permission_classes = [ClerkAuthenticated]
    def post(self, request):
        insta_post_link = request.data.get('post_link', '')
        images_link = request.data.get('image_url', '')
        post_description = request.data.get('description', '')
        social2amazon_data = {
            "post_link": insta_post_link,
            "image_url": images_link,
            "description": post_description
        }
        if not insta_post_link:
            return Response({
                "message": "Please provide a valid Instagram post link"
            })
        else:
            connected_social_media = ConnectedSocialMedia.objects.first()
            connected_social_media_count = 0

            if connected_social_media:
                links = [
                    connected_social_media.instagram_link,
                    connected_social_media.facebook_link,
                    connected_social_media.tiktok_link,
                ]
                connected_social_media_count = sum(1 for link in links if link.strip())

            if not connected_social_media or connected_social_media_count == 0:
                return Response({
                    "message": "Please connect your social media accounts"
                })
            else:
                GOOGLE_API_KEY = settings.GOOGLE_API_KEY
                social2amazon = Social2Amazon(GOOGLE_API_KEY=GOOGLE_API_KEY)
                product_data = social2amazon.process_post(social2amazon_data)
                product_title = product_data.get('product_title')
                product_title_hash = hash(product_title)
                if ProductListings.objects.filter(product_id=product_title_hash).exists():
                    ProductListings.objects.filter(product_id=product_title_hash).delete()
                
                # Make sure product_data has valid JSON or None for JSON fields
                if 'about this item' in product_data and not isinstance(product_data['about this item'], (dict, list)) and product_data['about this item']:
                    # Convert string to valid JSON or set to None
                    try:
                        import json
                        product_data['about this item'] = json.loads(product_data['about this item'])
                    except:
                        product_data['about this item'] = None

                if 'product_details' in product_data and not isinstance(product_data['product_details'], (dict, list)) and product_data['product_details']:
                    try:
                        import json
                        product_data['product_details'] = json.loads(product_data['product_details'])
                    except:
                        product_data['product_details'] = None

                ProductListings(
                    product_id=product_title_hash,
                    images_list=product_data.get('images_list'),
                    product_title=product_title,
                    price=product_data.get('price'),  # Keep as string
                    product_details=product_data.get('product_details'),
                    about_this_item=product_data.get('about this item'),
                    product_description=product_data.get('Product description')
                ).save()
                return Response({
                    "message": "Data added successfully",
                })

class HealthCheckAPI(APIView):
    """
    Endpoint to check API health without authentication
    """
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "healthy"})
