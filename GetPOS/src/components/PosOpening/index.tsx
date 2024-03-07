import React, { useEffect, useState, useContext } from "react";
import "./index.css";
import { useFrappeGetCall, useFrappePostCall } from "frappe-react-sdk";
import APIs from "../../constants/APIs";
import UserItemsContext from "../../common/cartContext";
import ModalBox from "../../common/popup";

const PosOpening = () => {
  const [visibility, setVisibility] = useState(false);
  const [profileMethods, setProfileMethods] = useState([]);
  const [posProfile, setPosProfile] = useState("");

  const popupCloseHandler = (e) => {
    setVisibility(e);
  };

  const { data, error, isLoading } = useFrappeGetCall(APIs.checkOpeningShift, {
    user: "Administrator",
  });

  console.log(data, "data");

  const {
    data: paymentMethods,
    error: paymentError,
    isLoading: loadingPaymentMethods,
  } = useFrappeGetCall(APIs.getPaymentMethods);

  console.log(paymentMethods, "Payment Methods");

  const cartListItems: any = useContext(UserItemsContext);

  useEffect(() => {
    if (posProfile) {
      const finalData = paymentMethods?.message?.payments_method.filter(
        (method) => method.parent === posProfile
      );
      setProfileMethods(finalData);
    }
  }, [posProfile]);

  // if (!isLoading && data?.message.length > 0) {
  //   setVisibility(true);
  // }

  const RenderOpenShift = () => {
    return (
      <div className="column pos-open-content">
        <select
          className="pos-open-input"
          onChange={(e) => setPosProfile(e.target.value)}
          value={posProfile}
        >
          <option disabled selected={true}>
            Select POS Profile
          </option>
          {paymentMethods?.message?.pos_profiles_data.map((profile) => {
            return <option value={profile.name}>{profile.name}</option>;
          })}
        </select>
        <table className="pos-open-table">
          <tbody>
            <tr>
              <th>Mode Of Payment</th>
              <th>Opening Balance</th>
            </tr>
            {profileMethods?.length > 0 &&
              profileMethods.map((pro) => {
                return (
                  <tr>
                    <td>
                      <input
                        value={pro?.mode_of_payment}
                        className="pos-open-table-input"
                        readOnly
                      />
                    </td>
                    <td>
                      <input className="pos-open-table-input" />
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div>
      {visibility === true && (
        <>
          <ModalBox
            onClose={popupCloseHandler}
            visibility={visibility}
            title="Open Shift"
            htmlRender={() => <RenderOpenShift />}
          />
        </>
      )}
    </div>
  );
};

export default PosOpening;
