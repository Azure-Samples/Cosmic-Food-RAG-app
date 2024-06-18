import { useState } from "react";

import { Modal, IconButton, DefaultButton, TextField, Dropdown, IDropdownOption } from "@fluentui/react";

import styles from "./BuyModal.module.css";
import { DataPoint } from "../../api";

interface Props {
    isBuy: boolean;
    setIsBuy: (isBuy: boolean) => void;
    address: string;
    setAddress: (address: string) => void;
    latestItems: DataPoint[];
    cartItems: string[];
    setCartItems: (cartItems: string[]) => void;
}

export const BuyModal = ({ setIsBuy, setAddress, isBuy, address, latestItems, cartItems, setCartItems }: Props) => {
    const [buyItem, setBuyItem] = useState<string>("");
    const [lastItem, setLastItem] = useState<string>("");

    const onAddressChange = (_ev: React.FormEvent<HTMLInputElement | HTMLTextAreaElement>, newValue?: string) => {
        if (!newValue) {
            setAddress("");
        } else {
            setAddress(newValue);
        }
    };

    const onItemChange = (_ev: React.FormEvent<HTMLDivElement>, option?: IDropdownOption<string> | undefined) => {
        setBuyItem(option?.data || "");
        if (option?.data && option.data && option.data.length > 0) {
            setLastItem(option.data);
        }
    };

    const updateItems = () => {
        if (lastItem && lastItem.length > 0) {
            setCartItems([...cartItems, lastItem]);
        }
        setIsBuy(false);
    };
    const labelWithCollection: string = `Selected Item to Buy from ${latestItems[0].collection}`;

    return (
        <Modal className={styles.buyContainer} isOpen={isBuy} onDismiss={() => setIsBuy(false)} isBlocking={true}>
            <div>
                <IconButton iconProps={{ iconName: "Cancel" }} ariaLabel="Close popup modal" onClick={() => setIsBuy(false)} />

                <div className={styles.buyContainer}>
                    <div className={styles.modalTitle}>
                        <h1>Confirm Selection</h1>
                    </div>
                </div>
                <div className={styles.buyContainer}>
                    <Dropdown
                        className={styles.buyInput}
                        label={labelWithCollection}
                        ariaLabel="Selected Item to Buy"
                        placeholder="Select an item to buy"
                        options={latestItems.flatMap((c, ind) => {
                            const option: IDropdownOption[] = [];
                            const parsed: string = `${c.price} - ${c.name}`;
                            option.push({ key: ind, text: parsed, data: parsed, selected: buyItem == parsed });
                            return option;
                        })}
                        required
                        onChange={onItemChange}
                    />
                </div>
                <div className={styles.buyContainer}>
                    <div className={styles.buyMessage}>Enter your address:</div>
                </div>
                <div className={styles.buyContainer}>
                    <TextField className={styles.buyInput} value={address} onChange={onAddressChange} multiline resizable={false} borderless />
                </div>
                <div className={styles.buyContainer}>
                    <DefaultButton className={styles.buyMessage} onClick={updateItems}>
                        Buy Now?
                    </DefaultButton>
                </div>
            </div>
        </Modal>
    );
};
