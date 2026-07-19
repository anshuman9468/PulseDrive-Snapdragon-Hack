package com.pulsedrive.di

import com.pulsedrive.data.remote.ApiService
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import javax.inject.Singleton

import com.pulsedrive.data.remote.DashboardApiService
import com.pulsedrive.data.remote.MonitorApiService
import com.pulsedrive.data.remote.AuthInterceptor
import com.pulsedrive.data.remote.AiApi
import com.pulsedrive.data.repository.DashboardRepository
import com.pulsedrive.data.repository.DashboardRepositoryImpl
import com.pulsedrive.data.repository.MonitorRepository
import com.pulsedrive.data.repository.MonitorRepositoryImpl
import com.pulsedrive.data.repository.AiRepository
import com.pulsedrive.data.repository.AiRepositoryImpl
import com.pulsedrive.data.repository.ServiceConciergeRepository
import com.pulsedrive.data.repository.ServiceConciergeRepositoryImpl

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        loggingInterceptor: HttpLoggingInterceptor,
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("http://10.245.6.60:8000/") // Local FastAPI Backend Base URL
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideDashboardApiService(retrofit: Retrofit): DashboardApiService {
        return retrofit.create(DashboardApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideDashboardRepository(apiService: DashboardApiService): DashboardRepository {
        return DashboardRepositoryImpl(apiService)
    }

    @Provides
    @Singleton
    fun provideMonitorApiService(retrofit: Retrofit): MonitorApiService {
        return retrofit.create(MonitorApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideMonitorRepository(apiService: MonitorApiService): MonitorRepository {
        return MonitorRepositoryImpl(apiService)
    }

    @Provides
    @Singleton
    fun provideAiApi(retrofit: Retrofit): AiApi {
        return retrofit.create(AiApi::class.java)
    }

    @Provides
    @Singleton
    fun provideAiRepository(aiApi: AiApi): AiRepository {
        return AiRepositoryImpl(aiApi)
    }

    @Provides
    @Singleton
    fun provideServiceConciergeRepository(apiService: ApiService): ServiceConciergeRepository {
        return ServiceConciergeRepositoryImpl(apiService)
    }
}
