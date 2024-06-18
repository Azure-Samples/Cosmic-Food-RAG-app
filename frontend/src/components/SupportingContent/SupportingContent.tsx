import styles from "./SupportingContent.module.css";

import { DataPoint } from "../../api";

interface Props {
    supportingContent: DataPoint[];
}

export const SupportingContent = ({ supportingContent }: Props) => {
    const textItems = supportingContent ? supportingContent : [];
    return (
        <ul className={styles.supportingContentNavList}>
            {textItems.map((c, ind) => {
                const parsed = c;
                return (
                    <li className={styles.supportingContentItem} key={ind}>
                        <h4 className={styles.supportingContentItemHeader}>
                            {parsed.name} ({parsed.category}) [{parsed.collection}]
                        </h4>
                        <p className={styles.supportingContentItemText} dangerouslySetInnerHTML={{ __html: parsed.description }} />
                        <p className={styles.supportingContentItemText}>{parsed.price}</p>
                    </li>
                );
            })}
        </ul>
    );
};
