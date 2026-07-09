const getCookie = (name: string) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        const part = parts.pop();
        if (part !== undefined) {
            return part.split(';').shift();
        }
    }
    return null;
}

export default getCookie;