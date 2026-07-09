// Add support for missing types// speech-recognition.d.ts

interface SpeechRecognition extends EventTarget {
    grammars: SpeechGrammarList;
    lang: string;
    continuous: boolean;
    interimResults: boolean;
    maxAlternatives: number;

    onaudioend: ((ev: Event) => void) | null;
    onaudiostart: ((ev: Event) => void) | null;
    onend: ((ev: Event) => void) | null;
    onerror: ((ev: SpeechRecognitionErrorEvent) => void) | null;
    onnomatch: ((ev: SpeechRecognitionEvent) => void) | null;
    onresult: ((ev: SpeechRecognitionEvent) => void) | null;
    onsoundend: ((ev: Event) => void) | null;
    onsoundstart: ((ev: Event) => void) | null;
    onspeechend: ((ev: Event) => void) | null;
    onspeechstart: ((ev: Event) => void) | null;
    onstart: ((ev: Event) => void) | null;

    abort(): void;
    start(): void;
    stop(): void;
}

interface SpeechRecognitionStatic {
    prototype: SpeechRecognition;
    new(): SpeechRecognition;
}

interface Window {
    SpeechRecognition: SpeechRecognitionStatic;
    webkitSpeechRecognition: {
        new(): SpeechRecognition;
        prototype: SpeechRecognition;
    };
}
  
type User = {
    user_id: number;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    is_admin: boolean;
}

type Domain = {
    domain_id: number;
    domain_name: string;
    prompts: string;
    datasets: Dataset[];
}

type DomainDataset = {
    domain_id: number;
    domain_name: string;
    datasets: Dataset[];
}

type Dataset = {
    dataset_id: number;
    dataset_name: string;
}

type DataSourceDataset = {
    dataset_id: number;
    name: string;
    file_type: string;
    domain_id: string;
}

type Message = {
    id: number;
    sender: string;
    text: string;
    timestamp: Date;
}

type AttachedFile = {
    file: File;
    name: string;
    size: number;
    type: string;
}