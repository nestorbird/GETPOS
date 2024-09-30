import React, { useEffect, useState, useContext } from 'react';
import { getItemByScan } from '../modules/LandingPage';
import { Modal } from 'antd';
import { CartContext } from '../common/CartContext';

const BarcodeScanner = () => {
    const [code, setCode] = useState("");
    let barcodeScan = "";

    const { addItemToCart } = useContext(CartContext);
    useEffect(() => {
        let scanTimeout;

        function handleKeyDown(e) {
            if (e.keyCode === 13 && barcodeScan.length > 3) {
                handleScan(barcodeScan);
                barcodeScan = "";
                clearTimeout(scanTimeout);
            } else if (e.keyCode !== 16) {
                barcodeScan += e.key;

                clearTimeout(scanTimeout);
                scanTimeout = setTimeout(() => {
                    barcodeScan = "";
                }, 200);
            }
        }

        document.addEventListener('keydown', handleKeyDown);

        return function cleanup() {
            document.removeEventListener('keydown', handleKeyDown);
            clearTimeout(scanTimeout);
        }
    }, []);

    const handleScan = async (barCodeString) => {
        setCode(barCodeString);
        await getItem(barCodeString); // Ensure getItem is awaited
    };

    const getItem = async (code) => {
        try {
            const res = await getItemByScan(code);
            if (res.status === 200) {
                console.log(res.data.message);
                const items = res.data.message[0].items;
                console.log(items,"Scanner")
                items.forEach(item => {
                    addItemToCart({
                        id: item.id,
                        name: item.name,
                        quantity: 1, // Default quantity
                        price: item.product_price // Corrected price property
                    });
                });
            } else {
                Modal.warning({
                    title: 'Item Not Found',
                    content: 'The scanned item was not found.',
                });
            }
        } catch (error) {
            Modal.error({
                title: 'Error',
                content: 'An error occurred while fetching the item.',
            });
        }
    };

    return (
        ""
    );
};

export default BarcodeScanner;
