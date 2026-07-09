import { createContext, useContext, useState, type Dispatch, type FC, type ReactNode, type SetStateAction } from 'react';

interface UsersDataContextType {
    users: User[] | null;
    setUsers: Dispatch<SetStateAction<User[] | null>>;
}

const UsersDataContext = createContext<UsersDataContextType | undefined>(undefined);

const UsersDataProvider: FC<{children: ReactNode}> = ({ children }) => {
    const [users, setUsers] = useState<User[] | null>(null);

    return (
        <UsersDataContext.Provider value={{ users, setUsers }}>
            { children }
        </UsersDataContext.Provider>
    );
};

const useUsersDataContext = (): UsersDataContextType => {
    const context = useContext(UsersDataContext);
    if (!context) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
};

export { UsersDataProvider, useUsersDataContext}
