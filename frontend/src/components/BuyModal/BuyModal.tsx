import { useState } from "react";

import {
    Dialog,
    DialogSurface,
    DialogBody,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Textarea,
    TextareaOnChangeData,
    Dropdown,
    Option,
    OptionOnSelectData,
    SelectionEvents
} from "@fluentui/react-components";
import { Dismiss24Regular } from "@fluentui/react-icons";

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

    const onAddressChange = (_ev: React.ChangeEvent<HTMLTextAreaElement>, data: TextareaOnChangeData) => {
        setAddress(data.value || "");
    };

    const onItemChange = (_ev: SelectionEvents, data: OptionOnSelectData) => {
        const value = data.optionValue || "";
        setBuyItem(value);
        if (value.length > 0) {
            setLastItem(value);
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
        <Dialog open={isBuy} onOpenChange={(_ev, data) => setIsBuy(data.open)}>
            <DialogSurface className={styles.buyContainer}>
                <DialogBody>
                    <DialogTitle
                        className={styles.modalTitle}
                        action={<Button appearance="subtle" icon={<Dismiss24Regular />} aria-label="Close popup modal" onClick={() => setIsBuy(false)} />}
                    >
                        Confirm Selection
                    </DialogTitle>
                    <DialogContent>
                        <div className={styles.buyContainer}>
                            <label htmlFor="buyItemDropdown">{labelWithCollection}</label>
                        </div>
                        <div className={styles.buyContainer}>
                            <Dropdown
                                id="buyItemDropdown"
                                className={styles.buyInput}
                                aria-label="Selected Item to Buy"
                                placeholder="Select an item to buy"
                                value={buyItem}
                                selectedOptions={buyItem ? [buyItem] : []}
                                onOptionSelect={onItemChange}
                            >
                                {latestItems.map((c, ind) => {
                                    const parsed: string = `${c.price} - ${c.name}`;
                                    return (
                                        <Option key={ind} value={parsed}>
                                            {parsed}
                                        </Option>
                                    );
                                })}
                            </Dropdown>
                        </div>
                        <div className={styles.buyContainer}>
                            <div className={styles.buyMessage}>Enter your address:</div>
                        </div>
                        <div className={styles.buyContainer}>
                            <Textarea className={styles.buyInput} value={address} onChange={onAddressChange} resize="none" />
                        </div>
                    </DialogContent>
                    <DialogActions>
                        <Button className={styles.buyMessage} onClick={updateItems}>
                            Buy Now?
                        </Button>
                    </DialogActions>
                </DialogBody>
            </DialogSurface>
        </Dialog>
    );
};
