import { API_BASE_URL } from '@/config';
import { useState, useRef } from "react"
import MultiSelectDropdown from "@/components/MultiSelectDropdown";
import Close from '@mui/icons-material/Close';
import CircularProgress from '@mui/material/CircularProgress';

const piiCategories = [
    "name",
    "contact_number",
    "address",
    "aadhaar_number",
    "ssn",
    "tax_identification_number",
    "drivers_license",
    "financial_account",
    "health_insurance_policy_number",
    "health_insurance_subscriber_id",
    "citizenship_status",
    "ethnic_affiliation",
    "email",
    "password",
    "dob",
    "facial",
    "other"
];

type MaskingTypes = {
    media: { text: string; value: string }[];
    document: { text: string; value: string }[];
    audio: { text: string; value: string }[];
}

const maskingTypes: MaskingTypes = {
    media: [
        {
            text: 'Blurring', value: 'blurring'
        },
        {
            text: 'Rectangular Box', value: 'rectangular_box'
        },
    ],
    document: [
        {
            text: 'Replacement', value: 'replacement'
        },
        {
            text: 'Named/numbered Replacement',
            value: 'named_replacement'
        },
        {
            text: 'Size-preserving Replacement',
            value: 'size_preserving'
        },

    ],
    audio: [
        {
            text: 'Beep',
            value: 'beep'
        }
    ]
}

const TempMain = () => {
    const [file, setFile] = useState<File | null>(null);
    const [maskingType, setMaskingType] = useState<string>('replacement');
    const [selectedCategory, setSelectedCategory] = useState<string[]>([]);
    const [uploadState, setUploadState] = useState<number>(0);
    const [isDragging, setIsDragging] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [processedFile, setProcessedFile] = useState<{
        blob: Blob | null;
        filename: string;
    }>({
        blob: null,
        filename: ""
    });

    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setUploadState(1);
        }
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);

        const droppedFile = e.dataTransfer.files?.[0];
        if (droppedFile) {
            setFile(droppedFile);
            setUploadState(1);
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleRemoveFile = () => {
        setFile(null);
        setUploadState(0);
    };

    const handleBrowseClick = () => {
        fileInputRef.current?.click();
    };

    const handleProcessClick = async () => {

        const formData = new FormData();

        setLoading(true);

        if (!file) return;
        if (selectedCategory.length === 0) {
            alert("Please select at least one PII category.");
            return;
        }

        formData.append("file", file); // binary file
        formData.append("highlight_mode", maskingType);
        formData.append("pii_category", selectedCategory.join(", "));
        const response = await fetch(`${API_BASE_URL}/upload/`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            console.error(error);
            alert(error.error || "Upload failed");
            setLoading(false);
            return;
        }

        const json = await response.json();

        // Base64 → Blob
        const base64Data = json.download.file_data;
        const filename = json.download.filename;

        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);

        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/octet-stream" });

        // Save final file
        setProcessedFile({
            blob,
            filename
        });

        setLoading(false);
        setUploadState(2); // Proceed to output screen
    };

    const downloadProcessedFile = () => {
        if (!processedFile.blob) return;

        const url = window.URL.createObjectURL(processedFile.blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = processedFile.filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    };

    const renderMaskTypes = () => {

        if (!file) return;
        let mType = "other";
        if (/\.(jpg|jpeg|png|gif|mp4|mov|pdf|ppt|pptx)$/i.test(file.name)) {
            mType = "media";
        }
        else if (/\.(csv|xlsx|docx|txt)$/i.test(file.name)) {
            mType = "document";
        }
        else if (/\.(wav|mp3)$/i.test(file.name)) {
            mType = "audio";
        }

        const masks = maskingTypes[mType as keyof typeof maskingTypes];

        return masks.map((mask) => (
            <label className="flex items-center space-x-2">
                <input
                    type="radio"
                    name="maskingType"
                    value={mask.value}
                    checked={maskingType === mask.value}
                    onChange={() => setMaskingType(mask.value)}
                    className=""
                />
                <span>{mask.text}</span>
            </label>
        ));
    };

    const renderUploader = () => {
        switch (uploadState) {
            case 0:
                return (
                    <div
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        className={`w-full h-[360px] border-2 ${isDragging ? 'border-orange-500 bg-orange-50' : 'border-dashed border-gray-300'
                            } rounded-xl p-8 shadow-sm flex flex-col justify-center items-center transition`}
                    >
                        <p className="text-lg font-medium mb-2 text-center">
                            Drag and drop your file <br />
                            <span className="text-orange-600 font-semibold">or browse to upload.</span>
                        </p>

                        <button
                            type="button"
                            className="mt-4 bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-md font-semibold cursor-pointer"
                            onClick={handleBrowseClick}
                        >
                            Upload your file
                        </button>

                        <input
                            title="file-input"
                            ref={fileInputRef}
                            type="file"
                            accept=".csv,.xlsx,.mp4,.ppt,.pptx,.jpeg,.jpg,.png,.pdf,.docx,.wav,.mp3"
                            onChange={handleFileChange}
                            className="hidden"
                        />

                        <p className="mt-4 text-sm text-gray-500">
                            CSV, XLSX, MP4, PPT, JPEG, PNG, PDF, DOCX formats supported
                        </p>

                        <p className="mt-6 text-xs text-gray-400 text-center">
                            By uploading your files, you agree to the Ascent{" "}
                            <span className="text-orange-600 underline cursor-pointer">Terms of use</span> and{" "}
                            <span className="text-orange-600 underline cursor-pointer">Privacy Policy</span>
                        </p>
                    </div>
                );

            case 1:
                return (
                    <div className="w-full h-[360px] rounded-xl border border-gray-300 p-6 shadow-md bg-white">
                        <h2 className="text-center text-2xl font-bold text-orange-600 !mb-2">Uploaded Files</h2>

                        <div className="w-full flex items-center justify-between border border-gray-200 rounded-md px-4 py-2 bg-gray-100">
                            <span className="text-gray-800 w-full text-ellipsis overflow-hidden whitespace-nowrap">📁 {file?.name || 'Selected File'}</span>
                            <button
                                type="button"
                                title='remove'
                                className="text-gray-500 hover:text-red-500 font-bold text-lg"
                                onClick={handleRemoveFile}
                            >
                                <Close />
                            </button>
                        </div>

                        <div className="mt-6">
                            <p className="font-semibold mb-2 w-full text-left">Select Masking Types</p>
                            <div className="flex space-x-6">
                                {
                                    renderMaskTypes()
                                }
                            </div>
                        </div>

                        <div className="mt-6">
                            {/*<p className="font-semibold mb-2 w-full text-left">Select PII Category</p>*/}
                            <MultiSelectDropdown
                                categories={piiCategories}
                                selected={selectedCategory}
                                onChange={setSelectedCategory}
                            />
                        </div>

                        <div className="mt-6 flex justify-center">
                            <button type="button" className="h-10 flex justify-center items-center bg-orange-500 text-white font-semibold px-6 py-2 rounded-full hover:bg-orange-600 transition cursor-pointer"
                                onClick={handleProcessClick} disabled={loading}>
                                {
                                    loading ?
                                        <div className='w-full h-full flex justify-center items-center gap-4'>
                                            <CircularProgress size={24} color='inherit' className='text-white' />
                                            Loading...
                                        </div> : 'Process File'
                                }
                            </button>
                        </div>
                    </div>
                );

            case 2:
                return (
                    <div className="w-full h-[360px] rounded-xl border border-gray-300 p-6 shadow-md bg-white flex flex-col justify-between relative">
                        {/* ❌ Cross Button */}
                        <button
                            type="button"
                            onClick={handleRemoveFile}
                            className="absolute top-3 right-4 text-gray-500 hover:text-red-500 font-bold text-xl"
                            title="Close"
                        >
                            <Close />
                        </button>

                        <h2 className="text-center text-2xl font-bold text-orange-600 mb-4">Converted Files</h2>

                        <div className="space-y-3 flex-1 overflow-y-auto mt-[24px]">
                            {processedFile && (
                                <div className="flex justify-between items-center bg-gray-100 px-4 py-2 rounded-md border border-gray-200">
                                    <div className="flex items-center gap-2">
                                        <span className="text-yellow-500 text-lg">📁</span>
                                        <span className="text-gray-800">{processedFile.filename}</span>
                                    </div>
                                    <a
                                        href={URL.createObjectURL(processedFile.blob!)}
                                        download={processedFile.filename}
                                        className="text-orange-500 hover:text-orange-700 text-xl"
                                        title="Download"
                                    >
                                        ⬇️
                                    </a>
                                </div>
                            )}
                        </div>

                        <div className="mt-4 flex justify-center">
                            {processedFile && (
                                <button
                                    type="button"
                                    onClick={downloadProcessedFile}
                                    className="bg-orange-500 text-white font-semibold px-6 py-2 rounded-full hover:bg-orange-600 transition"
                                >
                                    Download All
                                </button>
                            )}
                        </div>
                    </div>
                );



        }
    };

    return (
        <main className="py-16 w-full">
            <div className="w-full px-4 text-center">
                <h1 className="text-[48px] font-semibold leading-tight text-left px-28 w-full">
                    PII Obfuscation
                </h1>
                <h2 className="mt-4 text-left px-28 w-full">
                    Effortlessly mask sensitive information in your files and protect privacy.
                </h2>

                <div className="w-full flex md:flex-nowrap flex-wrap justify-center gap-10 items-center mt-10">
                    <div className="w-full max-w-[600px] flex justify-center">
                        <img
                            src="/images/hero.jpg"
                            alt="Data Security Illustration"
                            className="rounded-[20px] max-w-[600px] md:h-[360px] h-[300px] object-cover w-full"
                        />
                    </div>
                    <div className="max-w-[600px] w-full bg-white rounded-lg">
                        {renderUploader()}
                    </div>
                </div>
            </div>
        </main>
    );
};

export default TempMain;
