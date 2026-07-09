
import Footer from '@/components/Footer';
import Navbar from '@/components/Navbar';
import TempMain from '@/components/TempMain';
// import { API_BASE_URL, API_HOST } from '@/config';

const Main = () => {

    return (
        <>
            <Navbar />

            <div className="w-full h-[calc(100vh-80px)] overflow-y-scroll flex flex-col justify-start items-center">

                <TempMain />

                <section className="bg-[#FFF5EC] w-full py-16">
                    <div className="mx-auto text-center px-4 max-w-[1440px] md:px-20">
                        <h2 className="text-2xl md:text-3xl font-semibold text-gray-800 mb-16">
                            How it Works
                        </h2>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-[36px]">
                            <div className="flex flex-col items-center text-center space-y-3">
                                <div className="bg-orange-500 rounded-full p-4 shadow-md">
                                    <img
                                        src="/images/upload_logo.svg"
                                        alt="Masking"
                                        className=" w-[23px] h-[23px] object-contain"
                                    />
                                </div>
                                <h3 className="text-[24px] font-semibold text-gray-800">File Upload</h3>
                                <p className="text-[16px] text-gray-500">Upload multiple file formats</p>
                            </div>

                            <div className="flex flex-col items-center text-center space-y-3">
                                <div className="bg-white rounded-full p-4 shadow-md">
                                    <img
                                        src="/images/detection_logo.svg"
                                        alt="Masking"
                                        className=" w-[23px] h-[23px] object-contain"
                                    />
                                </div>
                                <h3 className="text-[24px] font-semibold text-gray-800">PII Detection</h3>
                                <p className="text-[16px] text-gray-500">AI-Powered Identification</p>
                            </div>

                            <div className="flex flex-col items-center text-center space-y-3">
                                <div className="bg-white rounded-full p-4 shadow-md">
                                    <img
                                        src="/images/masking_logo.svg"
                                        alt="Masking"
                                        className=" w-[23px] h-[23px] object-contain"
                                    />
                                </div>
                                <h3 className="text-[24px] font-semibold text-gray-800">Masking</h3>
                                <p className="text-[16px] text-gray-500">Customizable obfuscation</p>
                            </div>

                            <div className="flex flex-col items-center text-center space-y-3">
                                <div className="bg-white rounded-full p-4 shadow-md">
                                    <img
                                        src="/images/download_logo.svg"
                                        alt="Masking"
                                        className=" w-[23px] h-[23px] object-contain"
                                    />
                                </div>
                                <h3 className="text-[24px] font-semibold text-gray-800">Preview & Download</h3>
                                <p className="text-[16px] text-gray-500">Review and Export</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="py-20 px-4 md:px-20 max-w-[1440px]">
                    <div className="max-w-7xl mx-auto space-y-24">
                        {/* Feature 1 */}
                        <div className="flex flex-col-reverse md:grid md:grid-cols-2 gap-12 items-center">
                            <img
                                src="/images/smart_efficient_masking.jpg"
                                alt="PII Masking"
                                className="rounded-xl w-full md:h-[435px] h-[300px] object-cover"
                            />
                            <div>
                                <h2 className="text-[40px] font-semibold text-gray-800 leading-[48px]">
                                    Smart & Efficient <br />
                                    <span className="text-orange-500">PII Masking</span>
                                </h2>
                                <p className="mt-4 text-gray-600">
                                    Easily upload and process multiple file formats—including text, spreadsheets, images,
                                    and PDFs—with intelligent PII detection built in. Detect sensitive information in both
                                    text and visuals using advanced AI and OCR technology.
                                </p>
                            </div>
                        </div>


                        {/* Feature 2 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center md:flex-row-reverse">
                            <div>
                                <h2 className="text-[40px] font-semibold text-gray-800 leading-[48px]">
                                    <span className="text-orange-500">Advanced Masking</span> <br />
                                    Techniques
                                </h2>
                                <p className="mt-4 text-gray-600">
                                    Apply smart masking to images and videos with yellow paint or blur effects for
                                    enhanced privacy. <br />
                                    Mask sensitive data in documents using name replacement, size-preserving techniques,
                                    or general text redaction—tailored for compliance and clarity.
                                </p>
                            </div>
                            <img
                                src="/images/advanced_tech.jpg"
                                alt="Advanced Masking"
                                className="rounded-xl w-full md:h-[435px] h-[300px] object-cover"
                            />
                        </div>

                        <div className="flex flex-col-reverse md:grid md:grid-cols-2 gap-12 items-center">
                            <img
                                src="/images/futuristic-technology-concept (1).jpg"
                                alt="PII Masking"
                                className="rounded-xl w-full md:h-[435px] h-[300px] object-cover"
                            />
                            <div>
                                <h2 className="text-[40px] font-semibold text-gray-800 leading-[48px]">
                                    Lightning Fast <br />
                                    <span className="text-orange-500">and Accurate</span>
                                </h2>
                                <p className="mt-4 text-gray-600">
                                    AI-powered PII detection delivers high accuracy across formats, ensuring sensitive data is reliably identified.
                                    Optimized for speed, our system processes files quickly—minimizing wait times and maximizing productivity.
                                </p>
                            </div>
                        </div>


                        {/* Feature 2 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center md:flex-row-reverse">
                            <div>
                                <h2 className="text-[40px] font-semibold text-gray-800 leading-[48px]">
                                    <span className="text-orange-500">Wide Format</span> <br />
                                    Support
                                </h2>
                                <p className="mt-4 text-gray-600">
                                    Handles a wide range of file types including images, videos, PDFs, spreadsheets, and text files. <br />
                                    Delivers consistent performance and accuracy, regardless of format or complexity.
                                    Seamlessly serves diverse industries like healthcare, finance, legal, education, and more.

                                </p>
                            </div>
                            <img
                                src="/images/wide_format.jpg"
                                alt="Advanced Masking"
                                className="rounded-xl w-full md:h-[435px] h-[300px] object-cover"
                            />
                        </div>

                        {/* Feature 5 */}
                        <div className="flex flex-col-reverse md:grid md:grid-cols-2 gap-12 items-center">
                            <img
                                src="/images/futuristic-technology-concept (1).jpg"
                                alt="PII Masking"
                                className="rounded-xl w-full md:h-[435px] h-[300px] object-cover"
                            />
                            <div>
                                <h2 className="text-[40px] font-semibold text-gray-800 leading-[48px]">
                                    Privacy & Security <br />
                                    <span className="text-orange-500">Guaranteed</span>
                                </h2>
                                <p className="mt-4 text-gray-600">
                                    Your data is never stored or shared—privacy is our top priority.
                                    All files are processed securely in real time with end-to-end confidentiality.
                                    Designed to meet strict data protection and compliance standards.
                                </p>
                            </div>
                        </div>

                    </div>
                </section>

                <section className="bg-[#F1F8FF] py-16 px-4 md:px-20">
                    <div className="flex justify-start items-center flex-col gap-5 text-center max-w-[1440px]">
                        <h2 className="text-2xl md:text-3xl font-semibold text-gray-800 mb-12">
                            Protect What Matters - AI-Driven PII Detection & Masking
                        </h2>

                        <div className="w-full flex justify-center md:flex-row flex-col items-stretch md:px-10 px-2.5 gap-10">
                            {/* Media Files Card */}
                            <div className="relative bg-white rounded-xl p-6 text-left shadow-md w-full flex flex-col justify-between items-center min-h-[300px]">

                                <div className='w-full flex flex-col items-center justify-start'>
                                    {/* Tag */}
                                    <div className="absolute top-0 right-0">
                                        <div className="bg-orange-500 text-white text-xs px-3 py-1 rounded-bl-xl rounded-tr-xl font-semibold">
                                            Media
                                        </div>
                                    </div>

                                    <h3 className="text-orange-600 font-semibold text-lg mb-4">Media Files</h3>
                                    <p className="text-gray-700 text-sm mb-2">
                                        For JPG, JPEG, PNG, GIF, MP4, and PPT files, you can choose:
                                    </p>
                                    <ul className="text-sm text-gray-600 list-disc list-inside space-y-2 mb-6">
                                        <li>
                                            <strong>Yellow Paint Masking</strong> - Covers sensitive data with a solid yellow
                                            overlay
                                        </li>
                                        <li>
                                            <strong>Blur Masking</strong> - Applies a soft blur to obscure PII while keeping
                                            content readable
                                        </li>
                                    </ul>
                                </div>


                                <button className="bg-orange-500 text-white px-5 py-2 rounded-md text-sm font-medium hover:bg-orange-600 transition">
                                    Try Now
                                </button>
                            </div>

                            {/* Document Files Card */}
                            <div className="relative bg-white rounded-xl p-6 text-left shadow-md w-full flex flex-col justify-between items-center min-h-[300px]">
                                <div className='w-full flex flex-col items-center justify-start'>
                                    {/* Tag */}
                                    <div className="absolute top-0 right-0">
                                        <div className="bg-orange-500 text-white text-xs px-3 py-1 rounded-bl-xl rounded-tr-xl font-semibold">
                                            Documents
                                        </div>
                                    </div>

                                    <h3 className="text-orange-600 font-semibold text-lg mb-4">Document Files</h3>
                                    <p className="text-gray-700 text-sm mb-2">
                                        For PDF, CSV, XLSX, DOCX, and TXT files, we offer:
                                    </p>
                                    <ul className="text-sm text-gray-600 list-disc list-inside space-y-2 mb-6">
                                        <li>
                                            <strong>Name-Replacement Masking</strong> – Replaces sensitive names with generic
                                            placeholders.
                                        </li>
                                        <li>
                                            <strong>Size-Preserving Replacement Masking</strong> – Replaces PII while
                                            maintaining character length.
                                        </li>
                                        <li>
                                            <strong>Replacement Masking</strong> – Replaces PII with asterisks or predefined
                                            values.
                                        </li>
                                    </ul>
                                </div>


                                <button className="bg-orange-500 text-white px-5 py-2 rounded-md text-sm font-medium hover:bg-orange-600 transition">
                                    Try Now
                                </button>
                            </div>
                        </div>
                    </div>
                </section>
                <Footer />
            </div>
        </>
    );
};


export default Main;