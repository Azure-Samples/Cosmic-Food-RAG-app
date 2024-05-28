import { Cart24Regular } from "@fluentui/react-icons";
import { Button } from "@fluentui/react-components";

import styles from "./CartButton.module.css";

interface Props {
    className?: string;
    onClick: () => void;
}

export const CartButton = ({ className, onClick }: Props) => {
    return (
        <div className={`${styles.container} ${className ?? ""}`}>
            <Button icon={<Cart24Regular />} onClick={onClick}>
                {"Cart"}
            </Button>
        </div>
    );
};
