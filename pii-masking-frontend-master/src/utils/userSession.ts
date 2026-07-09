export const getUser = (): User | null => {
    const userData = sessionStorage.getItem('user');
    if(userData){
        const user = JSON.parse(userData) as User;
        return user;
    }
    return null
}