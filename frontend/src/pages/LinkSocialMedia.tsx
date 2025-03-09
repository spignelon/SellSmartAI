import React, { useEffect, useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import Modal from "./Modal";
import { Link } from 'react-router-dom';
import {
    enable as enableDarkMode,
    disable as disableDarkMode,
    exportGeneratedCSS as collectCSS,
    isEnabled as isDarkReaderEnabled,
} from 'darkreader';

// Define the type for the product data

type ProductData = {
    product_id: string;
    created_at: string;
    images_list: string[];
    product_title: string;
    price: string;
    product_details: { [key: string]: string };
    about_this_item: string;
    product_description: string;
    approved: boolean;
};
const LinkSocialMedia: React.FC = () => {
    // Code for Social media connection : start
    const { isLoaded, getToken, signOut } = useAuth();

    const [helloUser, setHelloUser] = useState(""); // State to store the hello user message
    const [error, setError] = useState<string | null>(null);
    const [profile_img, setProfileImg] = useState(null); // State to store the profile image

    // State to track whether the window is maximized or not
    const [isMaximized, setIsMaximized] = useState<boolean>(false);

    // Handle the button click to toggle the maximize state
    const handleMaximizeClick = () => {
        if (isMaximized) {
            document.exitFullscreen();
        } else {
            const elem = document.documentElement;
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            }
        }
        setIsMaximized((prevState) => !prevState);
    };

    // Function to fetch user data
    const getUsername = async () => {
        try {
            const token = await getToken();
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/profile_data`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );
            if (!response.ok) {
                throw new Error("Failed to fetch data");
            }
            const data = await response.json();
            if (data.first_name) {
                setHelloUser(data.first_name); // Update state with API response
                setProfileImg(data.profile_image); // Update state with API response
            } else {
                setError(data.message || "Unknown error occurred");
            }
        } catch (err: any) {
            setError(err.message);
        }
    };

    const [socialMediaLinks, setSocialMediaLinks] = useState({
        instagram_link: "",
        facebook_link: "",
        tiktok_link: "",
    });

    const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
    const [newLink, setNewLink] = useState<string>("");
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Fetch connected social media accounts
    const fetchSocialMediaLinks = async () => {
        try {
            const token = await getToken();
            const response = await fetch(`${import.meta.env.VITE_BACKEND_API_URL}/connected_social_media`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) {
                throw new Error("Failed to fetch social media links");
            }
            const data = await response.json();
            setSocialMediaLinks(data);
        } catch (error: any) {
            console.error("Error fetching social media links:", error.message);
        }
    };

    // Submit updated social media link
    const handleSubmit = async () => {
        if (!newLink || !selectedPlatform) return;

        const requestBody: { [key: string]: string } = {
            [`${selectedPlatform}_link`]: newLink,
        };

        try {
            const token = await getToken();
            const response = await fetch(`${import.meta.env.VITE_BACKEND_API_URL}/update_social_media`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestBody),
            });

            if (response.ok) {
                setSocialMediaLinks((prev) => ({
                    ...prev,
                    [`${selectedPlatform}_link`]: newLink,
                }));
                setIsModalOpen(false);
            } else {
                console.error("Error updating social media link");
            }
        } catch (error: any) {
            console.error("Error:", error.message);
        }
    };

    // Fetch social media links on component mount
    useEffect(() => {
        if (isLoaded) {
            getUsername();
            fetchSocialMediaLinks();
        }
    }, [isLoaded]);

    const openModal = (platform: string) => {
        setSelectedPlatform(platform);
        setNewLink("");
        setIsModalOpen(true);
    };

    const renderCard = (platform: string, link: string) => {
        const truncateLink = (link: string, maxLength: number) => {
            // Remove 'https://' or 'http://' prefix and truncate
            const cleanLink = link.replace(/^https?:\/\//, "").replace("www.", "").replace("instagram.com/", "@").replace("facebook.com/", "@").replace("tiktok.com/", "@");
            return cleanLink.length > maxLength
                ? `${cleanLink.slice(0, maxLength)}...`
                : cleanLink;
        };

        return (
            <div className="col-md-4">
                <div
                    className="d-flex flex-column align-items-center border rounded p-4"
                    style={{ fontFamily: "Open Sans, sans-serif" }}
                >
                    <div
                        className="rounded-circle bg-primary d-flex justify-content-center align-items-center text-white social-media-icon mb-3"
                        style={{ width: "60px", height: "60px" }}
                    >
                        <i className={`bi bi-${platform} fs-2`}></i>
                    </div>
                    <h6
                        className="mb-1 text-dark"
                        style={{ fontSize: "1.4rem", fontWeight: "600" }}
                    >
                        {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </h6>
                    {link ? (
                        <>
                            <p
                                className="mb-3 text-center"
                                style={{ fontSize: "1.3rem", lineHeight: "1.5" }}
                            >
                                Connected with the following account:
                                <br />
                                <a
                                    href={link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <span className="d-none d-lg-inline">
                                        {truncateLink(link, 20)} {/* For large screens */}
                                    </span>
                                    <span className="d-lg-none">
                                        {truncateLink(link, 15)} {/* For small screens */}
                                    </span>
                                </a>
                            </p>
                            <button
                                className="btn btn-outline-primary px-4 py-2 fw-bold"
                                style={{ fontSize: "1.2rem", fontWeight: "500" }}
                                onClick={() => openModal(platform)}
                            >
                                Change Account
                            </button>
                        </>
                    ) : (
                        <>
                            <p
                                className="text mb-3 text-center"
                                style={{ fontSize: "1.3rem", lineHeight: "1.5" }}
                            >
                                Connect your{" "}
                                {platform.charAt(0).toUpperCase() + platform.slice(1)}{" "}
                                account
                            </p>
                            <button
                                className="btn btn-outline-primary px-4 py-2 fw-bold"
                                style={{ fontSize: "1.2rem", fontWeight: "500" }}
                                onClick={() => openModal(platform)}
                            >
                                Connect
                            </button>
                        </>
                    )}
                </div>
            </div>
        );
    };

    // Code for social medai connection : end

    // code for post editing and preview : start
    // State for storing API data
    // State for storing API data
    const [productData, setProductData] = useState<ProductData | null>(null);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false); // Preview state
    const [formData, setFormData] = useState<Record<string, any>>({}); // Dynamic fields
    const [responseMessage, setResponseMessage] = useState<string>(""); // Response message state

    // Fetch data from `/recent_fetched_post` when the edit modal is opened
    useEffect(() => {
        if (isEditModalOpen) fetchProductData();
    }, [isEditModalOpen]);
    useEffect(() => {
        if (isLoaded) fetchProductData();
    }, [isLoaded]);
    // Fetch data from `/recent_fetched_post` when the edit modal is opened
    useEffect(() => {
        if (isEditModalOpen) fetchProductData();
    }, [isEditModalOpen]);
    useEffect(() => {
        if (isLoaded) fetchProductData();
    }, [isLoaded]);


    const fetchProductData = async () => {
        try {
            const token = await getToken(); // Assuming getToken retrieves a valid token
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/recent_fetched_post`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch product data");
            }

            const data = await response.json();
            if (data) {
                setProductData(data); // Set the first item of the array as productData
                setFormData(data); // Initialize the form with fetched data
            } else {
                throw new Error("No product data available");
            }
        } catch (err: any) {
            console.error("Error fetching product data:", err.message);
        }
    };

    // Handle dynamic form field changes
    const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    // Handle form submission
    const handleFormSubmit = async () => {
        try {
            // Get the authorization token.
            const token = await getToken();

            // Send the request using fetch and include the token in the headers
            const response = await fetch(`${import.meta.env.VITE_BACKEND_API_URL}/update_listing_data`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData), // Send form data as the request body
            });

            // Check if the response is successful
            if (response.ok) {
                setResponseMessage("Product data updated successfully!");
                setIsEditModalOpen(false); // Close the edit modal
                fetchProductData(); // Refresh the data after updating
            } else {
                console.error("Error updating product data");
                setResponseMessage("Error updating product data. Please try again.");
            }
        } catch (error: any) {
            console.error("Error:", error.message);
            setResponseMessage("Error updating product data. Please try again.");
        }
    };

    // code for post editing and preview : end

    // Code for Viewing previous listing : start
    const [productList, setProductList] = useState<ProductData[]>([]);
    const [isProductListLoaded, setIsProductListLoaded] = useState<boolean>(false);
    const [selectedProduct, setSelectedProduct] = useState<ProductData | null>(
        null
    ); // For modal display
    const [isProductModalOpen, setIsProductModalOpen] = useState<boolean>(false);

    const fetchPreviousListings = async () => {
        try {
            const token = await getToken(); // Replace with your authentication method
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/previous_listing_data`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch product listings");
            }

            const data = await response.json();
            setProductList(data);
            setIsProductListLoaded(true);
        } catch (err: any) {
            setError(err.message);
        }
    };

    const toggleApprovalStatus = async (product: ProductData) => {
        try {
            const updatedStatus = !product.approved;
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/update_listing_data`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${await getToken()}`,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ ...product, approved: updatedStatus }),
                }
            );

            if (!response.ok) {
                throw new Error("Failed to update approval status");
            }

            setProductList((prev) =>
                prev.map((item) =>
                    item.product_id === product.product_id
                        ? { ...item, approved: updatedStatus }
                        : item
                )
            );
        } catch (err: any) {
            setError(err.message);
        }
    };

    useEffect(() => {
        fetchPreviousListings();
    }, [isProductListLoaded]);

    // Code for viewing previous listing : end

    // Code for adding data in the databse
    type InstagramPost = {
        post_link: string;
        image_url: string[];
        video_url: string;
        description: string;
    };
    const [instagramLinks, setInstagramLinks] = useState<InstagramPost[]>([]);
    const [loadingPosts, setLoadingPosts] = useState(false);
    const [convertingLink, setConvertingLink] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    const fetchInstagramPosts = async () => {
        setLoadingPosts(true);
        setError(null);
        setSuccessMessage(null);

        try {
            const token = await getToken(); // Replace with your token retrieval method
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/fetch_latest_instagram_post`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch Instagram posts");
            }

            const data = await response.json();
            setInstagramLinks(data.post_links || []); // Assuming API returns an array of URLs
        } catch (err: any) {
            console.error("Error fetching Instagram posts:", err.message);
            setError(err.message || "An error occurred while fetching Instagram posts.");
        } finally {
            setLoadingPosts(false);
        }
    };

    // Convert Instagram post video link to images_list
    const ConvertVideoInstatoProjectListing = async (post_link: string | null, video_url: string, description: string) => {
        setConvertingLink(post_link);
        setError(null);
        try {
            const token = await getToken();
            const requestBody = {
                video_url: video_url
            };

            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/convert_video_to_images`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(requestBody),
                }
            );

            if (!response.ok) {
                throw new Error("Failed to convert Instagram post to product listing");
            }

            const data = await response.json();
            const image_url = data.quality_images;
            convertToProductListing(post_link, image_url, description);
            fetchPreviousListings();
            fetchProductData();
            setSuccessMessage(`Successfully converted to product listing: ${post_link}`);
        } catch (err: any) {
            console.error("Error converting to product listing:", err.message);
            setError(`Error converting to product listing for link: ${post_link}`);
        } finally {
            setConvertingLink(null);
        }
    }

    // Code for adding data in the databse
    type FacebookPost = {
        post_link: string;
        image_url: string[];
        description: string;
    };
    const [facebookLinks, setFacebookLinks] = useState<FacebookPost[]>([]);
    const [loadingFBPosts, setFBLoadingPosts] = useState(false);
    const [errorFB, setFBError] = useState<string | null>(null);
    const [successFBMessage, setFBSuccessMessage] = useState<string | null>(null);

    const fetchFacebookPosts = async () => {
        setFBLoadingPosts(true);
        setFBError(null);
        setSuccessMessage(null);

        try {
            const token = await getToken(); // Replace with your token retrieval method
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/fetch_latest_facebook_post`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch Facebook posts");
            }

            const data = await response.json();
            setFacebookLinks(data.post_links || []); // Assuming API returns an array of URLs
        } catch (err: any) {
            console.error("Error fetching Facebook posts:", err.message);
            setFBError(err.message || "An error occurred while fetching Facebook posts.");
        } finally {
            setFBLoadingPosts(false);
        }
    };

    const convertToProductListing = async (post_link: string | null, image_url: string[], description: string) => {
        setConvertingLink(post_link);
        setError(null);
        if (post_link?.includes("instagram")) {
            setSuccessMessage(null);
        } else {
            setFBSuccessMessage(null);
        }

        try {
            const token = await getToken(); // Replace with your token retrieval method
            const requestBody = {
                post_link: post_link,
                image_url: image_url, // list of string
                description: description // string
            };

            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/social2amazon`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(requestBody),
                }
            );

            if (!response.ok) {
                throw new Error("Failed to convert Instagram post to product listing");
            }
            fetchPreviousListings();
            fetchProductData();
            if (post_link?.includes("instagram")) {
                setSuccessMessage(`Successfully converted to product listing: ${post_link}`);
            } else {
                setFBSuccessMessage(`Successfully converted to product listing: ${post_link}`);
            }
        } catch (err: any) {
            console.error("Error converting to product listing:", err.message);
            setError(`Error converting to product listing for link: ${post_link}`);
        } finally {
            setConvertingLink(null);
        }
    };
    // Dark mode function
    const [darkMode, setDarkMode] = useState(false);

    const toggleDarkMode = () => {
        if (darkMode) {
            enableDarkMode({
                brightness: 100,
                contrast: 90,
                sepia: 10,
            });
        } else {
            disableDarkMode();
        }
        setDarkMode(!darkMode);
    };

    const handleCollectCSS = async () => {
        const css = await collectCSS();
        console.log(css); // Log or handle the generated CSS
    };

    const checkDarkModeStatus = () => {
        const isEnabled = isDarkReaderEnabled();
        console.log('Is Dark Mode enabled:', isEnabled);
    };

    return (
        <>
            <div id="wrapper">

                <div id="page" className="">
                    {/* layout-wrap  */}
                    <div className="layout-wrap">
                        {/* preload  */}
                        {/* <div id="preload" className="preload-container">
                        <div className="preloading">
                            <span></span>
                        </div>
                    </div>  */}
                        {/* preload section-menu-left  */}
                        <div className="section-menu-left">
                            <div className="box-logo">
                                <Link to="#" id="site-logo-inner">
                                    <img className="logo" src="images\logo\logo.png" alt="" />
                                </Link>
                                <div className="button-show-hide">
                                    <i className="icon-menu-left"></i>
                                </div>
                            </div>
                            <div className="center">
                                <div className="center-item">
                                    <ul className="menu-list">
                                        <li className="menu-item">
                                            <Link to="/" className="menu-item-button">
                                                <div className="icon"><i className="icon-home"></i></div>
                                                <div className="text">Home</div>
                                            </Link>
                                        </li>
                                        <li className="menu-item">
                                            <Link to="/dashboard" className="menu-item-button">
                                                <div className="icon"><i className="icon-grid"></i></div>
                                                <div className="text">Dashboard</div>
                                            </Link>
                                        </li>
                                        <li className="menu-item">
                                            <Link to="/linksocialmedia" className="">
                                                <div className="icon"><i className="icon-image"></i></div>
                                                <div className="text">Link Social Media</div>
                                            </Link>
                                        </li>
                                    </ul>
                                </div>
                            </div>

                        </div>
                        {/* section-menu-left  */}
                        {/* section-content-right  */}
                        <div className="section-content-right">
                            {/* header-dashboard  */}
                            <div className="header-dashboard">
                                <div className="wrap">
                                    <div className="header-left">
                                        <Link to="index.html">
                                            <img className="logo" id="logo_header_mobile" alt="" src="images/logo/logo.png" />
                                        </Link>
                                        <div className="button-show-hide">
                                            <i className="icon-menu-left"></i>
                                        </div>
                                    </div>
                                    <div className="btn d-inline-flex align-items-center justify-content-center shadow-sm rounded-full">
                                        <button onClick={toggleDarkMode}>
                                            {darkMode ? (
                                                <img
                                                    src="https://cdn-icons-png.flaticon.com/256/4445/4445942.png"
                                                    alt=""
                                                    className="w-8 h-8 rounded-full"
                                                />
                                            ) : (
                                                <img
                                                    src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_xqmYro3MAiVCYxvtXyjyx_MC4VYmNKVRqQ&s"
                                                    alt=""
                                                    className="w-8 h-8 rounded-full"
                                                />
                                            )}
                                        </button>

                                        <button onClick={handleCollectCSS}></button>
                                        <button onClick={checkDarkModeStatus}></button>

                                        {/* Optionally display the collected CSS */}
                                        {/* <pre>{collectedCSS}</pre> */}
                                    </div>
                                    <div className="header-grid">
                                        <div className="header-item button-zoom-maximize" onClick={handleMaximizeClick}>
                                            <div className="">
                                                <i className={`icon-maximize ${isMaximized ? 'maximized' : ''}`}></i>
                                            </div>
                                        </div>
                                        <div className="popup-wrap user type-header">
                                            <div className="dropdown">
                                                <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton3" data-bs-toggle="dropdown" aria-expanded="false">
                                                    <span className="header-user wg-user">
                                                        <span className="image">
                                                            {profile_img && <img src={profile_img} alt="" />}
                                                            {error && <img src="images/avatar/user-1.png" alt="" />}
                                                        </span>
                                                        <span className="flex flex-column">
                                                            <span className="text-tiny">Hello</span>
                                                            {helloUser && <span className="body-title mb-2">{helloUser}!</span>}
                                                            {error && <span className="body-title mb-2">Error: {error}!</span>}
                                                        </span>
                                                    </span>
                                                </button>
                                                <ul className="dropdown-menu dropdown-menu-end has-content" aria-labelledby="dropdownMenuButton3" >
                                                    <li>
                                                        <Link to="#" className="user-item">
                                                            <div className="icon">
                                                                <i className="icon-user"></i>
                                                            </div>
                                                            <div className="body-title-2">Account</div>
                                                        </Link>
                                                    </li>
                                                    <li>
                                                        <Link to="#" className="user-item">
                                                            <div className="icon">
                                                                <i className="icon-log-out"></i>
                                                            </div>
                                                            <div className="body-title-2" onClick={() => signOut()}>Log out</div>
                                                        </Link>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {/* header-dashboard  */}
                            {/* main-content  */}
                            <div className="main-content">
                                {/* main-content-wrap  */}
                                <div className="main-content-inner">
                                    {/* main-content-wrap  */}
                                    <div className="main-content-wrap">
                                        <div className="main-content-wrap">

                                            <div className="wg-box mb-30">
                                                <div>
                                                    <div className="container px-4 py-4">
                                                        <h4 className="mb-3 text-dark text-center" style={{ fontSize: "2rem", fontWeight: "600", fontFamily: "Roboto, sans-serif" }}>
                                                            Connect Your Social Media Accounts
                                                        </h4>
                                                        <p className="text-center mb-4" style={{ fontSize: "1.35rem", lineHeight: "1.6", fontFamily: "Open Sans, sans-serif" }}>
                                                            Link your accounts to start generating Amazon listings from your content.
                                                        </p>

                                                        {/* Social Media Cards */}
                                                        <div className="row gx-4">
                                                            {renderCard("instagram", socialMediaLinks.instagram_link)}
                                                            {renderCard("facebook", socialMediaLinks.facebook_link)}
                                                            {renderCard("tiktok", socialMediaLinks.tiktok_link)}
                                                        </div>

                                                        {/* Modal */}
                                                        {isModalOpen && (
                                                            <div className="modal fade show d-block" tabIndex={-1} style={{ backgroundColor: "rgba(0, 0, 0, 0.5)" }}>
                                                                <div className="modal-dialog">
                                                                    <div className="modal-content">
                                                                        <div className="modal-header">
                                                                            <h5 className="modal-title">
                                                                                Connect {selectedPlatform ? selectedPlatform.charAt(0).toUpperCase() + selectedPlatform.slice(1) : ''} Account
                                                                            </h5>
                                                                            <button type="button" className="btn-close" onClick={() => setIsModalOpen(false)}></button>
                                                                        </div>
                                                                        <div className="modal-body">
                                                                            <div className="form-group">
                                                                                <label htmlFor="socialMediaLink" className="form-label">Profile URL</label>
                                                                                <input
                                                                                    type="url"
                                                                                    id="socialMediaLink"
                                                                                    className="form-control"
                                                                                    value={newLink}
                                                                                    onChange={(e) => setNewLink(e.target.value)}
                                                                                />
                                                                            </div>
                                                                        </div>
                                                                        <div className="modal-footer">
                                                                            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>Close</button>
                                                                            <button type="button" className="btn btn-primary" onClick={handleSubmit}>Submit</button>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Add insta posts to database */}
                                            <div className="wg-box mb-30">
                                                <h1 className="text-lg font-bold text-center mb-6 flex items-center justify-center space-x-3">
                                                    <img className="h-20 w-20" src="https://png.pngtree.com/png-clipart/20180626/ourmid/pngtree-instagram-icon-instagram-logo-png-image_3584853.png" alt="Facebook Logo" />
                                                    <span>Convert Instagram Posts to Product Listings</span>
                                                </h1>

                                                <button
                                                    className={`btn btn-primary w-full mb-4 ${loadingPosts ? "opacity-50 cursor-not-allowed" : ""}`}
                                                    onClick={fetchInstagramPosts}
                                                    disabled={loadingPosts}
                                                >
                                                    {loadingPosts ? (
                                                        <span className="loader inline-block mr-2"></span>
                                                    ) : (
                                                        "Fetch Latest Instagram Posts"
                                                    )}
                                                </button>

                                                {error && <p className="text-red-500 text-center mt-2">{error}</p>}
                                                {successMessage && <p className="text-green-500 text-center mt-2">{successMessage}</p>}

                                                {instagramLinks.length > 0 && (
                                                    <table className="table-auto w-full border-collapse border border-gray-300 mt-6">
                                                        <thead>
                                                            <tr className="bg-gray-100 text-gray-700">
                                                                <th className="border border-gray-300 px-4 py-2">Instagram Post Link</th>
                                                                <th className="border border-gray-300 px-4 py-2">Action</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {instagramLinks.map((post, index) => (
                                                                <tr key={index} className="hover:bg-gray-50">
                                                                    <td className="border border-gray-300 px-4 py-2">
                                                                        <a
                                                                            href={post.post_link}
                                                                            target="_blank"
                                                                            rel="noopener noreferrer"
                                                                            className="text-blue-500 underline"
                                                                        >
                                                                            {post.post_link}
                                                                        </a>
                                                                    </td>
                                                                    <td className="border border-gray-300 px-4 py-2 text-center">
                                                                        <button
                                                                            className={`btn btn-primary ${convertingLink === post.post_link
                                                                                ? "opacity-50 cursor-not-allowed"
                                                                                : ""
                                                                                }`}
                                                                            onClick={() => {
                                                                                if (post.video_url) {
                                                                                    ConvertVideoInstatoProjectListing(post.post_link, post.video_url, post.description);
                                                                                } else {
                                                                                    convertToProductListing(post.post_link, post.image_url, post.description);
                                                                                }
                                                                            }}
                                                                            disabled={convertingLink === post.post_link}
                                                                        >
                                                                            {convertingLink === post.post_link ? (
                                                                                <span className="loader inline-block mr-2"></span>
                                                                            ) : (
                                                                                post.video_url ? (
                                                                                    <>
                                                                                        <i className="bi bi-camera-video me-2"></i> Convert to Product Listing
                                                                                    </>
                                                                                ) : (
                                                                                    <>
                                                                                        <i className="bi bi-file-earmark-post me-2"></i> Convert to Product Listing
                                                                                    </>
                                                                                )
                                                                            )}
                                                                        </button>
                                                                    </td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                )}
                                            </div>


                                            {/* Facebook to Amazon */}
                                            <div className="wg-box mb-30">
                                                <h1 className="text-lg font-bold text-center mb-6 flex items-center justify-center space-x-3">
                                                    <img className="h-20 w-20" src="https://www.logo.wine/a/logo/Facebook/Facebook-f_Logo-Blue-Logo.wine.svg" alt="Facebook Logo" />
                                                    <span>Convert Facebook Posts to Product Listings</span>
                                                </h1>


                                                <button
                                                    className={`btn btn-primary w-full mb-4 ${loadingFBPosts ? "opacity-50 cursor-not-allowed" : ""}`}
                                                    onClick={fetchFacebookPosts}
                                                    disabled={loadingFBPosts}
                                                >
                                                    {loadingFBPosts ? (
                                                        <span className="loader inline-block mr-2"></span>
                                                    ) : (
                                                        "Fetch Latest Facebook Posts"
                                                    )}
                                                </button>

                                                {errorFB && <p className="text-red-500 text-center mt-2">{errorFB}</p>}
                                                {successFBMessage && <p className="text-green-500 text-center mt-2">{successFBMessage}</p>}

                                                {facebookLinks.length > 0 && (
                                                    <table className="table-auto w-full border-collapse border border-gray-300 mt-6">
                                                        <thead>
                                                            <tr className="bg-gray-100 text-gray-700">
                                                                <th className="border border-gray-300 px-4 py-2">Instagram Post Link</th>
                                                                <th className="border border-gray-300 px-4 py-2">Action</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {facebookLinks.map((post, index) => (
                                                                <tr key={index} className="hover:bg-gray-50">
                                                                    <td className="border border-gray-300 px-4 py-2">
                                                                        <a
                                                                            href={post.post_link}
                                                                            target="_blank"
                                                                            rel="noopener noreferrer"
                                                                            className="text-blue-500 underline"
                                                                        >
                                                                            {post.post_link}
                                                                        </a>
                                                                    </td>
                                                                    <td className="border border-gray-300 px-4 py-2 text-center">
                                                                        <button
                                                                            className={`btn btn-primary ${convertingLink === post.post_link
                                                                                ? "opacity-50 cursor-not-allowed"
                                                                                : ""
                                                                                }`}
                                                                            onClick={() => convertToProductListing(post.post_link, post.image_url, post.description)}
                                                                            disabled={convertingLink === post.post_link}
                                                                        >
                                                                            {convertingLink === post.post_link ? (
                                                                                <span className="loader inline-block mr-2"></span>
                                                                            ) : (
                                                                                "Convert to Product Listing"
                                                                            )}
                                                                        </button>
                                                                    </td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                )}
                                            </div>

                                            <div className="wg-box mb-30 shadow-sm featured-content">
                                                <div className="">
                                                    <div className="row">
                                                        {/* Left Column: Carousel */}
                                                        <div className="col-md-6 mb-4 mb-md-0">
                                                            <div id="imageCarousel" className="carousel slide" data-bs-ride="carousel">
                                                                <div className="carousel-inner rounded">
                                                                    {productData?.images_list?.map((image, index) => (
                                                                        <div
                                                                            className={`carousel-item ${index === 0 ? "active" : ""}`}
                                                                            key={index}
                                                                        >
                                                                            <img
                                                                                src={`${import.meta.env.VITE_BASE_PATH}${image}`}
                                                                                className="d-block w-100"
                                                                                alt={`Slide ${index + 1}`}
                                                                            />
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                                <button
                                                                    className="carousel-control-prev"
                                                                    type="button"
                                                                    data-bs-target="#imageCarousel"
                                                                    data-bs-slide="prev"
                                                                >
                                                                    <span className="carousel-control-prev-icon" aria-hidden="true"></span>
                                                                    <span className="visually-hidden">Previous</span>
                                                                </button>
                                                                <button
                                                                    className="carousel-control-next"
                                                                    type="button"
                                                                    data-bs-target="#imageCarousel"
                                                                    data-bs-slide="next"
                                                                >
                                                                    <span className="carousel-control-next-icon" aria-hidden="true"></span>
                                                                    <span className="visually-hidden">Next</span>
                                                                </button>
                                                            </div>

                                                        </div>

                                                        {/* Right Column: Title, Description, and Buttons */}
                                                        <div className="col-md-6 d-flex flex-column">
                                                            <div>
                                                                <div className="featured-content-title">
                                                                    {productData?.product_title || "Loading Product Title ..."}
                                                                </div>
                                                                <p className="text-dark">
                                                                    {productData?.product_description
                                                                        ? productData.product_description.slice(0, 800) + "......."
                                                                        : "Loading Recent Imported Product Description ..."}
                                                                </p>
                                                            </div>
                                                            <div className="mt-16">
                                                                <p className="text-secondary-custom mb-3">
                                                                    {productData?.created_at
                                                                        ? "Fetched " + new Date(productData.created_at).toLocaleString()
                                                                        : "Fetching Created Date ..."}
                                                                </p>
                                                                {/* <p className="text-secondary-custom mb-3">
                                                                    Fetched {new Date(productData?.created_at).toLocaleString() || "some time ago"}
                                                                </p> */}
                                                                <div className="d-flex justify-content-end">
                                                                    <button
                                                                        className="btn btn-outline-primary me-2 link-btn"
                                                                        onClick={() => setIsPreviewModalOpen(true)}
                                                                    >
                                                                        Preview
                                                                    </button>
                                                                    <button
                                                                        className="btn btn-primary link-btn"
                                                                        onClick={() => setIsEditModalOpen(true)}
                                                                    >
                                                                        Edit Data
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        </div>


                                                        {/* Preview Modal */}
                                                        {isPreviewModalOpen && (
                                                            <div
                                                                className="modal-overlay d-flex align-items-center justify-content-center"
                                                                onClick={() => setIsPreviewModalOpen(false)}
                                                                style={{
                                                                    position: "fixed",
                                                                    top: 0,
                                                                    left: 0,
                                                                    width: "100vw",
                                                                    height: "100vh",
                                                                    backgroundColor: "rgba(0, 0, 0, 0.5)",
                                                                    zIndex: 1050,
                                                                }}
                                                            >
                                                                <div
                                                                    className="modal-content"
                                                                    onClick={(e) => e.stopPropagation()}
                                                                    style={{
                                                                        position: "relative",
                                                                        maxWidth: "90%",
                                                                        maxHeight: "90%",
                                                                        backgroundColor: "#fff",
                                                                        borderRadius: "8px",
                                                                        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                                                                        display: "flex",
                                                                        flexDirection: "column",
                                                                        overflow: "hidden",
                                                                    }}
                                                                >
                                                                    {/* Close Button */}
                                                                    <div
                                                                        style={{
                                                                            marginTop: "0px",
                                                                            textAlign: "right",
                                                                        }}
                                                                    >
                                                                        <button
                                                                            onClick={() => setIsPreviewModalOpen(false)}
                                                                            style={{
                                                                                background: "none",
                                                                                border: "none",
                                                                                fontSize: "1.5rem",
                                                                                cursor: "pointer",
                                                                            }}
                                                                            aria-label="Close"
                                                                        >
                                                                            &times;
                                                                        </button>
                                                                    </div>

                                                                    {/* Modal Content (Scrollable Area) */}
                                                                    <div
                                                                        style={{
                                                                            flex: 1,  // Allow the content area to grow and take available space
                                                                            overflowY: "auto",  // Enable vertical scrolling if content overflows
                                                                            padding: "20px",  // Optional: padding for the content
                                                                            maxHeight: "calc(90vh - 40px)",  // Make the content area scrollable with max height
                                                                        }}
                                                                    >
                                                                        {/* Pass productData to Modal component */}
                                                                        <Modal product={productData || { product_id: "", created_at: "", images_list: [], product_title: "", price: "", product_details: {}, about_this_item: "", product_description: "", approved: false, }} onClose={() => setIsPreviewModalOpen(false)} />
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}

                                                        {/* Edit Modal */}
                                                        {isEditModalOpen && (
                                                            <div className="modal-overlay" onClick={() => setIsEditModalOpen(false)}>
                                                                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                                                                    <h5>Edit Product Data</h5>
                                                                    <form>
                                                                        <label>
                                                                            Product Title:
                                                                            <input
                                                                                type="text"
                                                                                name="product_title"
                                                                                value={formData.product_title || ""}
                                                                                onChange={handleFormChange}
                                                                            />
                                                                        </label>
                                                                        <label>
                                                                            Product Description:
                                                                            <textarea
                                                                                name="product_description"
                                                                                value={formData.product_description || ""}
                                                                                onChange={handleFormChange}
                                                                            />
                                                                        </label>
                                                                        <label>
                                                                            About this Product:
                                                                            <textarea
                                                                                name="about_this_item"
                                                                                value={formData.about_this_item || ""}
                                                                                onChange={handleFormChange}
                                                                            />
                                                                        </label>
                                                                        <label>
                                                                            Price:
                                                                            <input
                                                                                type="text"
                                                                                name="price"
                                                                                value={formData.price || ""}
                                                                                onChange={handleFormChange}
                                                                            />
                                                                        </label>

                                                                        <button type="button" onClick={handleFormSubmit}>
                                                                            Submit
                                                                        </button>
                                                                        <button type="button" onClick={() => setIsEditModalOpen(false)}>
                                                                            Cancel
                                                                        </button>
                                                                    </form>

                                                                    {/* Response Message */}
                                                                    {responseMessage && <div className="response-message">{responseMessage}</div>}
                                                                </div>
                                                            </div>
                                                        )}


                                                    </div>
                                                </div>
                                            </div>
                                            {/* Linked Content Preview Section  */}
                                            {/* Product Added Section */}
                                            <div className="wg-box py-5 mb-30">
                                                <div className="text-center featured-content-title mb-4">
                                                    Previously Added Products
                                                </div>
                                                <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                                                    {error ? (
                                                        <div className="col">
                                                            <p className="text-danger">Error: {error}</p>
                                                        </div>
                                                    ) : (
                                                        productList.map((product) => (
                                                            <div className="col" key={product.product_id}>
                                                                <div
                                                                    className="card h-100 shadow-sm d-flex flex-column"
                                                                    style={{
                                                                        display: 'flex',
                                                                        flexDirection: 'column',
                                                                        height: '100%',
                                                                    }}
                                                                >
                                                                    <div className="card-img-container">
                                                                        <img
                                                                            src={`${import.meta.env.VITE_BASE_PATH}${product.images_list[0]}` || "default-image.jpg"}
                                                                            className="card-img-top"
                                                                            alt={product.product_title || "Product Image"}
                                                                        />
                                                                    </div>
                                                                    <div className="card-body d-flex flex-column" style={{ flexGrow: 1 }}>
                                                                        <h5 className="card-title added-products-title">
                                                                            {product.product_title || "Unknown Product"}
                                                                        </h5>
                                                                        <p className="card-text">
                                                                            Price: {product.price ? product.price : "N/A"}
                                                                        </p>
                                                                        <p className="card-text">
                                                                            Brand: {product.product_details?.Brand || "N/A"}
                                                                        </p>
                                                                        <p className="card-text">
                                                                            {product.about_this_item
                                                                                ? product.about_this_item.slice(0, 100) + (product.about_this_item.length > 100 ? "..." : "")
                                                                                : "Description not available"}
                                                                        </p>
                                                                    </div>
                                                                    <div className="card-footer d-flex justify-content-between">
                                                                        <div>
                                                                            <button
                                                                                className="btn btn-info"
                                                                                onClick={() => {
                                                                                    setSelectedProduct(product);
                                                                                    setIsProductModalOpen(true);
                                                                                }}
                                                                            >
                                                                                Preview
                                                                            </button>
                                                                        </div>
                                                                        <div className="text-center">
                                                                            <span className="text-s">Listing Status : </span>
                                                                            <button
                                                                                className={`btn ${product.approved ? "btn-success" : "btn-warning"}`}
                                                                                onClick={() => toggleApprovalStatus(product)}
                                                                            >
                                                                                {product.approved ? "Approved" : "Disapproved"}
                                                                            </button>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        ))
                                                    )}
                                                </div>

                                                {/* Modal Overlay */}
                                                {isProductModalOpen && selectedProduct && (
                                                    <div
                                                        className="modal-overlay"
                                                        onClick={() => setIsProductModalOpen(false)}  // Close on click outside
                                                        style={{
                                                            position: "fixed",
                                                            top: 0,
                                                            left: 0,
                                                            width: "100vw",
                                                            height: "100vh",
                                                            backgroundColor: "rgba(0, 0, 0, 0.5)",
                                                            display: "flex",
                                                            alignItems: "center",
                                                            justifyContent: "center",
                                                            zIndex: 1050,
                                                        }}
                                                    >
                                                        <div
                                                            className="modal-content"
                                                            onClick={(e) => e.stopPropagation()}  // Prevent modal from closing when clicked inside
                                                            style={{
                                                                position: "relative",
                                                                maxWidth: "90%",
                                                                maxHeight: "90%",
                                                                backgroundColor: "#fff",
                                                                borderRadius: "8px",
                                                                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                                                                display: "flex",
                                                                flexDirection: "column",
                                                                overflow: "hidden",
                                                                padding: "16px",
                                                            }}
                                                        >
                                                            {/* Close Button */}
                                                            <div
                                                                style={{
                                                                    position: "absolute",
                                                                    top: "10px",
                                                                    right: "10px",
                                                                }}
                                                            >
                                                                <button
                                                                    onClick={() => setIsProductModalOpen(false)}
                                                                    style={{
                                                                        background: "none",
                                                                        border: "none",
                                                                        fontSize: "1.5rem",
                                                                        cursor: "pointer",
                                                                        color: "#000",
                                                                    }}
                                                                    aria-label="Close"
                                                                >
                                                                    &times;
                                                                </button>
                                                            </div>

                                                            {/* Scrollable Content */}
                                                            <div
                                                                style={{
                                                                    flex: 1,
                                                                    overflowY: "auto",
                                                                    padding: "16px",
                                                                }}
                                                            >
                                                                <Modal product={selectedProduct} onClose={() => setIsProductModalOpen(false)} />
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}


                                            </div>

                                        </div>
                                        {/* main-content-wrap  */}
                                    </div>
                                    {/* main-content-wrap  */}
                                    {/* bottom-page  */}
                                    <div className="bottom-page">
                                        <div className="body-text">Made</div>
                                        {/* <i className="icon-heart"></i> */}
                                        <div className="body-text">by: <Link to="#">Ujjawal and Arushi.</Link> All rights reserved.</div>
                                    </div>
                                    {/* bottom-page  */}
                                </div>
                                {/* main-content  */}
                            </div>
                            {/* section-content-right  */}
                        </div>
                        {/* layout-wrap  */}
                    </div>
                    {/* page  */}
                </div>
            </div>

        </>
    );
};

export default LinkSocialMedia;
