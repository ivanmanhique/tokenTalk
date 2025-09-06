import { useEffect , useCallback , useState} from "react";

const useFetch = (API_LINK)=>{
      const [data, setData] = useState(null);
    const [error, setError] = useState(false);
    const [loading, setLoading] = useState(false);

    const callData = useCallback(async () => {
            setLoading(true);
            setError(false);

            try{
                    const response = await fetch(API_LINK);
                    if(!response.ok) throw new Error("Oups something is wrong !!! Can't fetch APi");
                    const  getDATA = await response.json();
                    setData(getDATA);
            }
            catch(err){
                    console.error(err);
                    setError(true);
            }
            finally{
                setLoading(false);
            }

    },[API_LINK])

    useEffect(()=>{
        callData();
    },[callData]);


        return { data, error, loading, callData };
}
export default useFetch;
