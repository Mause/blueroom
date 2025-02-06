
/* 
 * Decompiled with CFR 0.0. 
 *  
 * Could not load the following classes: 
 *  java.lang.Object 
 *  java.lang.String 
 *  retrofit2.Call 
 *  retrofit2.http.Body 
 *  retrofit2.http.GET 
 *  retrofit2.http.Headers 
 *  retrofit2.http.POST 
 *  retrofit2.http.Path 
 *  retrofit2.http.Query 
 */ 
package tickets.ferve.android.MIFF.rest; 
 
import retrofit2.Call; 
import retrofit2.http.Body; 
import retrofit2.http.GET; 
import retrofit2.http.Headers; 
import retrofit2.http.POST; 
import retrofit2.http.Path; 
import retrofit2.http.Query; 
import tickets.ferve.android.MIFF.model.Data; 
import tickets.ferve.android.MIFF.model.Init; 
import tickets.ferve.android.MIFF.model.InitResult; 
import tickets.ferve.android.MIFF.model.Login; 
import tickets.ferve.android.MIFF.model.LoginResult; 
import tickets.ferve.android.MIFF.model.WishlistList; 
 
public interface DataApiService { 
    @Headers(value={"Content-Type: application/json;charset=UTF-8"}) 
    @POST(value="apiApp/Account/Login") 
    public Call<LoginResult> accountLogin(@Body Login var1); 
 
    @GET(value="apiApp/Account/Delete") 
    public Call<String> deleteAccount(@Query(value="hash") String var1, @Query(value="hash2") String var2, @Query(value="hash3") String var3); 
 
    @GET(value="apiApp/Account/Sample") 
    public Call<LoginResult> getAccount(@Query(value="source") String var1); 
 
    @GET(value="apiApp/Account/Logout") 
    public Call<String> getAccountLogout(@Query(value="hash") String var1); 
 
    @GET(value="apiApp/Account/Reset") 
    public Call<String> getAccountReset(@Query(value="hash") String var1, @Query(value="email") String var2); 
 
    @GET(value="apiApp/Account/Token") 
    public Call<String> getAccountToken(@Query(value="hash") String var1, @Query(value="token") String var2, @Query(value="deviceId") String var3); 
 
    @GET(value="apiApp/Account/Update") 
    public Call<String> getAccountUpdate(@Query(value="hash") String var1); 
 
    @GET(value="apiApp/Account/Wishlist") 
    public Call<WishlistList> getAccountWishlist(@Query(value="hash") String var1, @Query(value="itemId") int var2, @Query(value="mode") String var3, @Query(value="location") String var4); 
 
    @GET(value="apiApp/Data") 
    public Call<Data> getData(@Query(value="lastUpdated") String var1); 
 
    @GET(value="apiApp/Cache/Cache/Data") 
    public Call<Data> getDataCache(); 
 
    @GET(value="apiApp/Init") 
    public Call<Data> getInit(@Query(value="source") String var1); 
 
    @Headers(value={"Content-Type: application/json;charset=UTF-8"}) 
    @POST(value="apiApp/Init") 
    public Call<InitResult> getInit(@Body Init var1, @Query(value="source") String var2); 
 
    @GET(value="apiApp/Account/MediaStream") 
    public Call<String> getMediaStream(@Query(value="hash") String var1, @Query(value="id") int var2); 
 
    @GET(value="apiApp/Content/MenuClicked") 
    public Call<String> getMenuClicked(@Query(value="hash") String var1, @Query(value="area") String var2, @Query(value="title") String var3); 
 
    @GET(value="movie/{id}") 
    public Call<Data> getMovieDetails(@Path(value="id") int var1, @Query(value="api_key") String var2); 
 
    @GET(value="apiApp/Content/PageView") 
    public Call<String> getPageView(@Query(value="hash") String var1); 
 
    @GET(value="apiApp/Vote/Check") 
    public Call<String> getVoteCheck(@Query(value="hash") String var1, @Query(value="itemId") int var2); 
 
    @GET(value="apiApp/Vote") 
    public Call<String> registerVote(@Query(value="hash") String var1, @Query(value="itemId") int var2, @Query(value="rating") int var3, @Query(value="ticketHash") String var4); 
} 
 
 
